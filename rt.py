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

def listRt(vpcId):
    rt_filter = [
        {
            'Name': 'vpc-id',
            'Values': [str(vpcId)]
        }
    ]

    # Delete Route Tables
    listRt = []
    rts = ec2client.describe_route_tables(Filters=rt_filter)

    for rt in rts['RouteTables']:
        rtAssociations = rt['Associations']
        if rtAssociations == []:
            listRt.append(rt['RouteTableId'])
        else:
            if all(element == 'false' for element in rtAssociations):
                listRt.append(rt['RouteTableId'])
    return listRt

def main():
    rt = listRt("vpc-0025569625a6b36eb")

    for r in rt:
        print(r)
   
if __name__ == "__main__":
    main()
