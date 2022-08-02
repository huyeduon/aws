#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Delete tgw attachment 
# Delete tgw route table 
# Delete tgw
# Terminate all instances
# Delete all subnets
# Delete custom security groups 
# Delete custom route tables
# Detach any internet gateways or virtual private gateways
# Delete VPC

from email.policy import default
from urllib import response
import logging
import boto3
import sys
from botocore.config import Config
from botocore.exceptions import ClientError
import time
# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

htduong = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong')
ec2 = session.resource('ec2', config=htduong)
ec2client = session.client('ec2', config=htduong)


custom_filter = [
    {
        'Name': 'tag:AciOwnerTag',
        'Values': ['?*']
    }
]


def listIgw():
    """
    return a list of Internet Gateways with properties State and VPC ID
    """
    listIgwInfo = []
    igws = ec2client.describe_internet_gateways(Filters=custom_filter)
    for x2 in igws['InternetGateways']:
        #print(x2)
        #print(x2['Attachments'])
        igwInfo = {}
        if x2['Attachments']:
            igwInfo['Id'] = x2['InternetGatewayId']

            igwInfo['State'] = x2['Attachments'][0]['State']
            igwInfo['VpcId'] = x2['Attachments'][0]['VpcId']
            listIgwInfo.append(igwInfo)
        else:
            print('Internet Gateway is detached.')

    return listIgwInfo

def main():
    listIgw()
   
if __name__ == "__main__":
    main()
