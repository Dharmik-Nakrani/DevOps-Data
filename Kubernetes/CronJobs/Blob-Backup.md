# Backup Blob Storage using Azure CLI and Kubernetes CronJob

## Generating SAS Tokens for Storage Accounts

To allow access to Azure Blob Storage, generate SAS tokens for different containers with appropriate permissions.

### Generate Read and List SAS Token for Source Container:

```sh
az storage container generate-sas --account-name cdncoreintegritydev \
  --name files --permissions rl \
  --expiry $(date -u -d "+365 days" '+%Y-%m-%dT%H:%M:%SZ') \
  --https-only --output tsv 
```

**Explanation:**

- `--account-name`: Specifies the storage account name.
- `--name`: Defines the container name.
- `--permissions rl`: Grants read (`r`) and list (`l`) permissions.
- `--expiry`: Sets the expiration date for the SAS token.
- `--https-only`: Ensures secure HTTPS-only access.
- `--output tsv`: Outputs the SAS token in tab-separated format.

### Generate Read, Write, Delete, List, and Create SAS Token for Backup Container:

```sh
az storage container generate-sas --account-name coreintegritybkup \
  --name files --permissions rwdlc \
  --expiry $(date -u -d "+365 days" '+%Y-%m-%dT%H:%M:%SZ') \
  --https-only --output tsv 
```

**Explanation:**

- Includes additional permissions: `w` (write), `d` (delete), and `c` (create).
- This allows full control over the container, making it suitable for backups.

### Generate SAS Token for Trash Container:

```sh
az storage container generate-sas --account-name coreintegritybkup \
  --name trash --permissions rwdlc \
  --expiry $(date -u -d "+365 days" '+%Y-%m-%dT%H:%M:%SZ') \
  --https-only --output tsv 
```

**Explanation:**

- The Trash container holds deleted files, requiring full permissions.

## Creating Kubernetes Namespace for Backup

To organize backup resources, create a dedicated namespace:

```sh
kubectl create namespace backup
```

**Explanation:**

- `kubectl create namespace backup`: Creates a namespace called `backup` to isolate resources.

## Creating a Secret for SAS Tokens

Store the generated SAS tokens in a Kubernetes Secret for secure access:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: blob-secret-prod
  namespace: backup
type: Opaque
data:
  SOURCE_STORAGE_ACCOUNT: "c3Rjb3JlaW50ZWdyaXR5cHJvZA=="
  SOURCE_SAS_TOKEN: "<Base64-encoded SAS token>"
  DEST_STORAGE_ACCOUNT: "Y29yZWludGVncml0eWJrdXBwcm9k"
  DEST_SAS_TOKEN: "<Base64-encoded SAS token>"
  TRASH_SAS_TOKEN: "<Base64-encoded SAS token>"
```

**Explanation:**

- `type: Opaque`: Stores sensitive data in a secure format.
- SAS tokens are Base64-encoded for security.

## Creating a Kubernetes CronJob for Blob Storage Sync

The following CronJob runs daily at 3 AM UTC to sync files between the source and destination storage accounts, moving deleted files to a Trash container.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: blob-backup-sync-trash
  namespace: backup
spec:
  schedule: "0 3 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: azcopy-sync
            image: debian:latest
            env:
            - name: SOURCE_STORAGE_ACCOUNT
              valueFrom:
                secretKeyRef:
                  name: blob-secret-prod
                  key: SOURCE_STORAGE_ACCOUNT
            - name: SOURCE_SAS_TOKEN
              valueFrom:
                secretKeyRef:
                  name: blob-secret-prod
                  key: SOURCE_SAS_TOKEN
            - name: DEST_STORAGE_ACCOUNT
              valueFrom:
                secretKeyRef:
                  name: blob-secret-prod
                  key: DEST_STORAGE_ACCOUNT
            - name: DEST_SAS_TOKEN
              valueFrom:
                secretKeyRef:
                  name: blob-secret-prod
                  key: DEST_SAS_TOKEN
            - name: TRASH_SAS_TOKEN
              valueFrom:
                secretKeyRef:
                  name: blob-secret-prod
                  key: TRASH_SAS_TOKEN
            command:
              - /bin/sh
              - -c
              - |
                echo "Installing dependencies..."
                apt-get update && apt-get install -y curl jq

                echo "Downloading and installing AzCopy..."
                curl -sL https://aka.ms/downloadazcopy-v10-linux | tar -xz
                mv azcopy_linux_amd64_*/azcopy /usr/local/bin/azcopy
                chmod +x /usr/local/bin/azcopy
                rm -rf azcopy_linux_amd64_*

                # List all files in the source after syncing
                azcopy list "https://${SOURCE_STORAGE_ACCOUNT}.blob.core.windows.net/files?${SOURCE_SAS_TOKEN}"  | grep -o '"name":"[^"]*"' | awk -F':' '{print $2}' | tr -d '"' > /tmp/source_files.txt

                # List all files in the destination before syncing
                azcopy list "https://${DEST_STORAGE_ACCOUNT}.blob.core.windows.net/files?${DEST_SAS_TOKEN}"  | grep -o '"name":"[^"]*"' | awk -F':' '{print $2}' | tr -d '"' > /tmp/destination_files.txt
                                
                # Sync new and modified files
                azcopy sync "https://${SOURCE_STORAGE_ACCOUNT}.blob.core.windows.net/files?${SOURCE_SAS_TOKEN}" \
                            "https://${DEST_STORAGE_ACCOUNT}.blob.core.windows.net/files?${DEST_SAS_TOKEN}" --recursive
                                
                # Find deleted files (files in destination but not in source)
                grep -Fxvf /tmp/source_files.txt /tmp/destination_files.txt > /tmp/deleted_files.txt
                
                # Move deleted files to Trash container
                while read file; do
                  echo "Moving deleted file: $file to Trash"
                  azcopy copy "https://${DEST_STORAGE_ACCOUNT}.blob.core.windows.net/files/${file}?${DEST_SAS_TOKEN}" \
                              "https://${DEST_STORAGE_ACCOUNT}.blob.core.windows.net/trash/${file}?${DEST_SAS_TOKEN}"
                  
                  # Remove the file from the destination after copying to Trash
                  azcopy remove "https://${DEST_STORAGE_ACCOUNT}.blob.core.windows.net/files/${file}?${DEST_SAS_TOKEN}"
                done < /tmp/deleted_files.txt
          restartPolicy: Never
```

## Explanation

- **AzCopy Installation**: Downloads and installs AzCopy for data transfer.
- **Blob Sync**: Copies all files from the source to the destination.
- **Deleted File Detection**: Compares file lists and identifies missing files.
- **Move to Trash**: Transfers deleted files to a separate Trash container.
- **Automation**: Runs daily at 3 AM to ensure backups are up to date.
