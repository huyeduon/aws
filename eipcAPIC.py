#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: huyeduon@cisco.com
# Requirements: python3, boto3, aws cli
# Delete tgw attachment
# Delete tgw route table
# Delete tgw
# Terminate all instances
# Delete all subnets
# Delete custom security groups
# Delete custom route tables
# Detach any internet gateways or virtual private gateways
# Delete VPC
# Delete Cloud APIC CFT Templates

import logging
from random import randrange
import boto3
import sys
from botocore.config import Config
import time
from alive_progress import alive_bar

htduong = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong')
ec2client = session.client('ec2', config=htduong)
cftclient = session.client('cloudformation', config=htduong)

def listEip():
    """
    return a list of IP
    """
    eip_filter = [
        {
            'Name': 'tag:AciOwnerTag',
            'Values': ['?*']
        }
    ]

    listEipInfo = []
    eip_response = ec2client.describe_addresses(Filters=eip_filter)
    eips = eip_response['Addresses']
    print(eips)
    for eip in eips:
        eipInfo = {}
        eipInfo['PublicIp'] = eip['PublicIp']
        eipInfo['AllocationId'] = eip['AllocationId']
        if 'AssociationI' in eip:
            eipInfo['AssociationId'] = eip['AssociationId']
        else:
            eipInfo['AssociationId'] = None
        listEipInfo.append(eipInfo)

    return listEipInfo



def listcApicEip():
    """
    return a list of IP
    """
    capic_filter = [
        {
            'Name': 'tag:aws:cloudformation:logical-id',
            'Values': ['rCAPICElasticIP']
        }
    ]
    listcApicEipInfo = []

    capic_response = ec2client.describe_addresses(Filters=capic_filter)
    eips = capic_response['Addresses']
    print(eips)
    for eip in eips:
        eipInfo = {}
        eipInfo['PublicIp'] = eip['PublicIp']
        eipInfo['AllocationId'] = eip['AllocationId']
        if 'AssociationId' in eip:
            eipInfo['AssociationId'] = eip['AssociationId']
        else:
            eipInfo['AssociationId'] = None
        listcApicEipInfo.append(eipInfo)

    return listcApicEipInfo

def main():
    
    cApicEip = listcApicEip()
    print(cApicEip)
    for ip in cApicEip:
        if ip['AssociationId'] != None:
            print('Nothing')


if __name__ == "__main__":
    main()
