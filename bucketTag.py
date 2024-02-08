#!/usr/bin/env python

import boto3
from botocore.config import Config

htduong = Config(
    region_name='us-east-1',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong')
s3 = session.client('s3', config=htduong)

def bucketTagging():

    bucket_tagging = s3.BucketTagging("nijnagoinsbu")
    tags =bucket_tagging.tag_set


    tags.append({'Key': 'DataClassification', 'Value': 'Cisco Public'})
    tags.append({'Key': 'IntendedPublic', 'Value': True})

    Set_Tag = bucket_tagging.put(Tagging={'TagSet': tags})

def main():

    bucketTagging()

if __name__ == main():
    main()
