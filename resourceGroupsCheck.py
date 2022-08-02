#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Requirements: python3, boto3, aws cli
# This script is used for inventory

import logging
from random import randrange
import boto3
import sys
from botocore.config import Config
import time
from alive_progress import alive_bar

htduong03 = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong03')
ec2client = session.client('ec2', config=htduong03)
cftclient = session.client('cloudformation', config=htduong03)
resourcesclient = session.client('resource-groups', config=htduong03)

def listResourceGroup():
    listRg = []
    listCapicRg = []
    resources = resourcesclient.list_groups()
   
    listRg.append(resources['GroupIdentifiers'][0]['GroupName'])
    for rg in listRg:
        if 'CAPIC' in rg:
            listCapicRg.append(rg)
    return listCapicRg


def delete_group(rg):
    response = resourcesclient.delete_group(Group=rg)


def main():
    
    print("Checking resources group")
    listCapicRg = listResourceGroup()
    for rg in listCapicRg:
        print(rg)
        delete_group(rg)

if __name__ == "__main__":
    main()
