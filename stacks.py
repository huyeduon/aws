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
#cloudformation = session.resource('cloudformation')


def aliveBar(x, sleepSpeed=0.05, title=''):
    with alive_bar(int(x), title=str(title)) as bar:   # default setting
        for i in range(int(x)):
            time.sleep(float(sleepSpeed))
            bar()

def listCftStack():
    response = cftclient.describe_stacks()
    stacks = response['Stacks']
    listStackName = []
    for stack in stacks:
        listStackName.append(stack['StackName'])
    return listStackName

def capic(stackName):
    capic = cftclient.describe_stacks(StackName = stackName)
    # x1 is a list
    x1 = capic['Stacks']
    capicText = 'This template creates the environment to launch a cloud APIC cluster in an AWS environment.'
    
    for x2 in x1:
        try:
            if x2['Description'] and capicText in x2['Description']:
                return True
        except KeyError:
                exit()

def capicStackToFile(listStackName):  
    for stackName in listStackName:
        if capic(stackName):
            return stackName
    
def delStack(StackName):
    cftclient.delete_stack(StackName=StackName)

def main():
    listStackName = listCftStack()
    cftcapic = capicStackToFile(listStackName)  
    print('Delete Cloud formation template', cftcapic)
    delStack(cftcapic)

    # progressive bar
    aliveBar(3000, 0.05, 'Delete cft template...')
if __name__ == "__main__":
    main()
    