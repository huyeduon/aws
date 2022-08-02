#!/usr/bin/env python
# -*- coding: utf-8 -*-
# delete tgw attachment first
# delete tgw route table

import boto3
import sys
from botocore.config import Config
import string


htduong = Config(
    region_name='us-east-1',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong')
s3 = session.client('s3', config=htduong)

'''
buckets = response['Buckets']
for bucket in buckets:
    print(bucket['Name'])
'''

source = "source-" + string.ascii_lowercase
destination = "dest-" + string.ascii_lowercase
print(source)
print(destination)

def createBuckets():

    sbucket = s3.create_bucket(
    ACL='public-read-write',
    Bucket=source,
    CreateBucketConfiguration={
        'LocationConstraint': 'us-west-1'
    }
    )

    dbucket = s3.create_bucket(
        ACL='public-read-write',
        Bucket=destination,
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-1'
        }
    )
''''
def deleteBuckets():
    s3.delete_bucket(Bucket=source)
    s3.delete_bucket(Bucket=destination)
'''
def main():
    createBuckets()
   # deleteBuckets()

if __name__ == main():
    pass
