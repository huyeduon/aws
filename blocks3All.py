#!/usr/bin/env python

import boto3
from botocore.config import Config

profileNames = ['htduong', 'htduong01', 'htduong02', 'htduong03', 'htduong04','htduong05', 'htduong06', 'htduong07','htduong08','htduong09']


def blockAccess():
    for profile in profileNames:
        session = boto3.session.Session(profile_name=profile)
        s3 = session.client('s3', config=profile)
        allbuckets = s3.list_buckets()

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
    print('Block all public access')
    blockAccess()


if __name__ == "__main__":
    main()
