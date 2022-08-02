#!/bin/bash 
acctA="htduong"
source="source"$(openssl rand -hex 6)
echo $source

destination="dest"$(openssl rand -hex 6)
echo $destination
sourceReg="us-east-1"
destReg="us-west-2 "

replicationRole="replicationRole"$(openssl rand -hex 6)


echo "Create source bucket"
aws s3api create-bucket \
--bucket $source \
--region $sourceReg \
--profile $acctA


aws s3api put-bucket-versioning \
--bucket $source \
--versioning-configuration Status=Enabled \
--profile $acctA


echo "Create destination bucket"
aws s3api create-bucket \
--bucket $destination \
--region $destReg \
--create-bucket-configuration LocationConstraint=$destReg \
--profile $acctA

aws s3api put-bucket-versioning \
--bucket $destination \
--versioning-configuration Status=Enabled \
--profile $acctA


echo "Create IAM role"
aws iam create-role \
--role-name $replicationRole \
--assume-role-policy-document file://s3-role-trust-policy.json  \
--profile $acctA