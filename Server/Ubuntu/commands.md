# Useful Linux Commands

This file contains various Linux commands for managing files, directories, processes, and network operations.

---

## 1. Create a TAR File

### Exclude Specific Files or Patterns
```bash
tar --exclude={} -zcvf images.tar.gz img/ welcome*
```
### Compress the entire development directory into a .tar.gz file:

```bash
tar -zcvf dev.tar.gz development/
```
---

## 2. Find File or Folder 

### Search the entire file system for files or directories matching a pattern:
```bash
find / --name "*regex*"
```
---

## 3. Find Content Within File 

### Recursively search for the string /auth/login in files within the current directory:
```bash
grep -R /auth/login *
```
---

## 4. Find Size of Directory 

### Check the size of the /var/lib/jenkins directory in a human-readable format:
```bash
sudo du -sh /var/lib/jenkins/
```
---

## 5. Secure File Transfer with scp 

### Transfer a file to a remote server using scp with a PEM file for authentication:
```bash
scp -i Documents/Project/ontofamily/ontofamily.pem <file> ubuntu@<ip>
```
---

## 6. Manage Running Ports and Processes 

### Check which processes are actively listening on ports:
```bash
sudo lsof -i -P -n | grep LISTEN
```
### Terminate a process running on a specific port (e.g., 8000):
```bash
sudo kill -9 $(sudo lsof -t -i:8000)
```