#!/usr/bin/env python
# -*- coding: utf-8 -*-
# delete tgw attachment first
# delete tgw route table

import boto3
import sys
from botocore.config import Config

htduong = Config(
    region_name='us-east-1',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong')
s3client = session.client('s3', config=htduong)
response = s3client.list_buckets()

buckets = response['Buckets']
for bucket in buckets:
    print(bucket)

client = boto3.client('s3')
