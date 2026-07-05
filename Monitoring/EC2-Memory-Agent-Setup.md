# AWS EC2 CloudWatch Monitoring Setup Guide

This guide explains two methods to enable **CloudWatch monitoring on EC2 instances**:

* **Method 1:** Using legacy CloudWatch monitoring scripts
* **Method 2 (Recommended):** Using Amazon CloudWatch Agent with IAM Role & SSM

---

# Prerequisites

* EC2 instance (Ubuntu/Linux)
* AWS CLI configured *(if using Method 1)*
* IAM permissions

---

# Method 1: Using CloudWatch Monitoring Scripts (Legacy)

## Step 1: Install Required Packages

```bash
sudo apt-get update
sudo apt-get install unzip -y
sudo apt-get install libwww-perl libdatetime-perl -y
```

---

## Step 2: Download Monitoring Scripts

```bash
curl https://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.2.zip -O
unzip CloudWatchMonitoringScripts-1.2.2.zip
rm CloudWatchMonitoringScripts-1.2.2.zip
cd aws-scripts-mon
```

---

## Step 3: Configure AWS Credentials

```bash
sudo mv awscreds.template awscreds.conf
sudo vim awscreds.conf
```

Add your credentials:

```ini
AWSAccessKeyId=YOUR_ACCESS_KEY
AWSSecretKey=YOUR_SECRET_KEY
```

**Warning:** Avoid hardcoding credentials in production. Use IAM Roles instead.

---

## Step 4: Test Monitoring Script

```bash
./mon-put-instance-data.pl --mem-util --verify --verbose
```

---

## Step 5: Send Metrics

```bash
./mon-put-instance-data.pl --mem-util --disk-space-util --disk-path=/
```

---

## Step 6: Setup Cron Job

```bash
crontab -e
```

Add:

```bash
*/5 * * * * ~/aws-scripts-mon/mon-put-instance-data.pl --mem-util --disk-space-util --disk-path=/ --from-cron
```

---

## Step 7: Help Command

```bash
~/aws-scripts-mon/mon-put-instance-data.pl --help
```

---

# Method 2: Using CloudWatch Agent (Recommended)

## Step 1: Create IAM Role

Attach the following policies to your EC2 role:

* `CloudWatchAgentServerPolicy`
* `AmazonSSMManagedInstanceCore`

Attach this role to your EC2 instance.

---

## Step 2: Install CloudWatch Agent via SSM

Go to **AWS Systems Manager → Run Command**

### Configuration:

* **Document Name:** `AWS-ConfigureAWSPackage`
* **Package Name:** `AmazonCloudWatchAgent`
* **Targets:** Select your EC2 instance

---

## Step 3: Create Parameter Store Config

Go to **AWS Systems Manager → Parameter Store**

### Create Parameter:

* **Name:** `AmazonCloudWatch-LinuxConfig`
* **Type:** String
* **Value:**

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
  },
  "metrics": {
    "metrics_collected": {
      "mem": {
        "measurement": [
          { "name": "used", "rename": "MemoryUsed" },
          { "name": "mem_available", "rename": "MemoryAvailable" }
        ]
      }
    },
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}"
    }
  }
}
```

---

## Step 4: Start CloudWatch Agent

Create another **Run Command**:

* **Document Name:** `AmazonCloudWatch-ManageAgent`
* **Action:** `configure`
* **Optional Configuration Location:** `AmazonCloudWatch-LinuxConfig`
* **Targets:** Select your EC2 instance

---

# Verification

* Go to **CloudWatch → Metrics**
* Check:

  * Memory Utilization
  * Disk Utilization

---

# Best Practices

* ✅ Use IAM Roles instead of hardcoded credentials
* ✅ Prefer CloudWatch Agent over legacy scripts
* ✅ Use Parameter Store for centralized config
* ✅ Enable detailed monitoring for better insights

---

# Summary

| Method           | Use Case             | Recommendation    |
| ---------------- | -------------------- | ----------------- |
| Script-based     | Legacy setups        |  Not recommended |
| CloudWatch Agent | Production workloads | Recommended     |

