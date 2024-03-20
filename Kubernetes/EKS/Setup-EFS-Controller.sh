#!/bin/bash
# Guide: https://aws.amazon.com/premiumsupport/knowledge-center/eks-persistent-storage/
echo "Enter Cluster Name:"
read cname

echo "Enter Account No:"
read accno

echo "Region:"
read reg

echo "EFS Id:"
read fs

curl -o iam-policy-example.json https://raw.githubusercontent.com/kubernetes-sigs/aws-efs-csi-driver/master/docs/iam-policy-example.json

aws iam create-policy \
    --policy-name AmazonEKS_EFS_CSI_Driver_Policy \
    --policy-document file://iam-policy-example.json
    
eksctl create iamserviceaccount \
    --cluster $cname \
    --namespace kube-system \
    --name efs-csi-controller-sa \
    --attach-policy-arn arn:aws:iam::$accno:policy/AmazonEKS_EFS_CSI_Driver_Policy \
    --approve \
    --region $reg
    
helm repo add aws-efs-csi-driver https://kubernetes-sigs.github.io/aws-efs-csi-driver/

helm repo update

helm upgrade -i aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver \
    --namespace kube-system \
    --set image.repository=602401143452.dkr.ecr.$reg.amazonaws.com/eks/aws-efs-csi-driver \
    --set controller.serviceAccount.create=false \
    --set controller.serviceAccount.name=efs-csi-controller-sa
    
wget https://eksworkshop.com/beginner/190_efs/efs.files/efs-pvc.yaml

sed -i "s/EFS_VOLUME_ID/$fs/g" efs-pvc.yaml
sed -i "s/namespace: storage/ /g" efs-pvc.yaml

kubectl apply -f efs-pvc.yaml
kubectl delete ns storage

kubectl get pvc

kubectl get pv



