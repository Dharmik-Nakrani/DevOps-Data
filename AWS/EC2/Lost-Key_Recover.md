Here is a complete and properly structured **Markdown (`.md`)** document titled `Recover-EC2-Access-Without-PEM.md`:

---

```markdown
# 🛠️ Recover EC2 Access Without PEM Key

If you’ve lost the `.pem` key for your AWS EC2 instance and SSM is **not enabled**, you can still regain access by mounting the root volume on another (helper) instance and adding a new SSH key.

---

## 📋 Prerequisites

- The original EC2 instance is **stopped** (not terminated).
- You have access to **another EC2 instance** (helper) with:
  - SSH access using a working PEM key.
  - Same Availability Zone as the original instance.
- You can access the AWS Console.

---

## 🧭 Step-by-Step Recovery Guide

### 1. 🛑 Stop the Inaccessible Instance

1. Go to **EC2 > Instances**.
2. Select the locked-out instance.
3. Click `Actions > Instance State > Stop`.

---

### 2. 📦 Detach the Root Volume

1. Go to **EC2 > Volumes (EBS)**.
2. Find the volume attached to your stopped instance.
3. Click `Actions > Detach Volume`.

---

### 3. 🔁 Attach Volume to Helper Instance

1. Go to **Volumes**, select the detached volume.
2. Click `Actions > Attach Volume`.
3. Attach to your helper instance (e.g., `/dev/sdf` or default `/dev/nvme1n1`).

---

### 4. 🔐 Connect to Helper Instance

SSH into the helper instance using your working `.pem` file:

```bash
ssh -i helper-key.pem ec2-user@<helper-instance-public-ip>
```

---

### 5. 🗃️ Mount the Attached Volume

```bash
sudo lsblk
```

> Look for a device like `/dev/nvme1n1p1`.

Then mount it:

```bash
sudo mkdir -p /mnt/recovery
sudo mount /dev/nvme1n1p1 /mnt/recovery
```

---

## 🔑 Step 6: Generate New Key Pair and Extract Public Key

### Option A: Create from AWS Console

1. Go to **EC2 > Key Pairs > Create key pair**
2. Name: `recovery-key`
3. File format: `.pem`
4. Save the file: `recovery-key.pem`

Extract public key:

```bash
ssh-keygen -y -f recovery-key.pem
```

Copy the output (starting with `ssh-rsa...`)

---

### Option B: Generate Locally

```bash
ssh-keygen -t rsa -b 2048 -f mykey
```

- `mykey` = private key
- `mykey.pub` = public key

Get the public key:

```bash
cat mykey.pub
```

---

## 🔧 Step 7: Add Public Key to Original Volume

Edit the `authorized_keys` file in the mounted volume:

For Amazon Linux:
```bash
sudo nano /mnt/recovery/home/ec2-user/.ssh/authorized_keys
```

For Ubuntu:
```bash
sudo nano /mnt/recovery/home/ubuntu/.ssh/authorized_keys
```

Paste the public key. Then set correct permissions:

```bash
sudo chmod 700 /mnt/recovery/home/ec2-user/.ssh
sudo chmod 600 /mnt/recovery/home/ec2-user/.ssh/authorized_keys
sudo chown -R ec2-user:ec2-user /mnt/recovery/home/ec2-user/.ssh
```

> Replace `ec2-user` with `ubuntu` if you're using Ubuntu.

---

## 🔁 Step 8: Detach and Reattach Volume

1. Run:
```bash
sudo umount /mnt/recovery
```

2. In AWS Console:
   - Detach the volume from the helper instance.
   - Reattach it to the original instance as **/dev/xvda** or **/dev/sda1**.

---

## 🚀 Step 9: Start Original Instance and Connect

Start your original instance and SSH in:

```bash
ssh -i recovery-key.pem ec2-user@<original-instance-public-ip>
```

---

## ✅ Optional: Enable SSM for Future Access

Once you have access:

1. Attach IAM role with `AmazonSSMManagedInstanceCore` to the instance.
2. Start the SSM agent:

```bash
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
```

---

## 🧠 Best Practices

- Always backup `.pem` files in a secure place.
- Enable **SSM Session Manager** on all instances.
- Consider creating a bastion host or VPN gateway for access management.

---

## 🔚 You're Done!

You have successfully recovered access to your EC2 instance without using the original PEM key.

```

---

Let me know if you'd like me to save this `.md` file and provide a downloadable version.
