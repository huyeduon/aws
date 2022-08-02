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

session = boto3.session.Session(profile_name='htduong02')
ec2client = session.client('ec2', config=htduong)
cftclient = session.client('cloudformation', config=htduong)


def listcAicEni():
    """
    return a cAPIC ENI
    """
    capicEni_filter = [
        {
            'Name': 'tag:aws:cloudformation:logical-id',
            'Values': ['rCAPICInfraInterface']
        }
    ]

    listcApicEni = []

    response = ec2client.describe_network_interfaces(
        Filters=capicEni_filter)
    capicEni = response['NetworkInterfaces']
    for eni in capicEni:
        listcApicEni.append(eni['NetworkInterfaceId'])

    return listcApicEni

def main():
    eni = listcAicEni()
    for e in eni:
        print(e)

if __name__ == "__main__":
    main()
