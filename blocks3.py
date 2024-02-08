#!/usr/bin/env python

import boto3
from botocore.config import Config

htduong09 = Config(
    region_name='us-east-1',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong09')
s3 = session.client('s3', config=htduong09)

# Output the bucket names
def listBuckets():
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')

def blockAccess():
    allbuckets = s3.list_buckets()
    # Iterate over the list
    for bucket in allbuckets['Buckets']:
        try:
            # This will set the public block settings
            s3.put_public_access_block(
                Bucket=bucket['Name'],
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
        except:
            pass
def main():

    print('Existing buckets:')
    listBuckets()
    print('Block all public access')
    blockAccess()

if __name__ == main():
    main()
