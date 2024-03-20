#!/bin/bash

echo "Enter Cluster Name:"
read cname

echo "Enter S3 Arn:"
read s3arn

echo "Enter AccNo:"
read accno


echo '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::12test123321"
        },
        {
            "Sid": "List",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
            "Resource": "arn:aws:s3:::12test123321/*"
        }
    ]
}' > s3_policy.json

aws iam create-policy \
    --policy-name EKSClusterS3AccessPolicy \
    --policy-document file://s3_policy.json
    
eksctl create iamserviceaccount \
  --name eks-s3-controller \
  --cluster $cname \
  --attach-policy-arn arn:aws:iam::$accno:policy/EKSClusterS3AccessPolicy \
  --approve
  
 
