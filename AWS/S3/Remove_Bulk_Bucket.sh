#!/bin/bash

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null
then
    echo "AWS CLI not found. Please install it first."
    exit 1
fi

# List all buckets starting with 'uh'
echo "Fetching buckets starting with 'uh'..."
buckets=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, 'uh')].Name" --output text)

if [ -z "$buckets" ]; then
    echo "No buckets starting with 'uh' found."
    exit 0
fi

# Display buckets to be deleted
echo "Buckets to be deleted:"
echo "$buckets"

# Confirm deletion
read -p "Are you sure you want to delete these buckets? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Deletion canceled."
    exit 0
fi

# Loop through and delete buckets
for bucket in $buckets
do
    echo "Emptying and deleting bucket: $bucket"

    # Empty the bucket first
    aws s3 rm s3://$bucket --recursive

    # Delete the bucket
    aws s3api delete-bucket --bucket $bucket

    echo "Deleted bucket: $bucket"
done

echo "All matching buckets have been deleted."
