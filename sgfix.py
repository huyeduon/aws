#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3
# -*- coding: utf-8 -*-

# Requirements: python3, boto3, aws cli
# This script is used for inventory

import logging
from random import randrange
import boto3
import argparse
from botocore.config import Config
import time
from alive_progress import alive_bar


# Define ec2client as a global variable
ec2client = None

def initialize_clients(profile_name, region_name):
    """
    Initialize AWS clients with the provided profile and region.
    """
    global ec2client
    session = boto3.session.Session(profile_name=profile_name, region_name=region_name)
    ec2client = session.client('ec2')


### custom filter
custom_filter = [
    {
        'Name': 'tag:AciOwnerTag',
        'Values': ['?*']
    }
]
### end of custom filter

def aliveBar(x, sleepSpeed=0.05, title=''):
    with alive_bar(int(x), title=str(title)) as bar:   # default setting
        for i in range(int(x)):
            time.sleep(float(sleepSpeed))
            bar()

def separator():
    print("======================================================================================================")


def listInstance():
    """
    return a list of TGW has tag key=owner, value=huyen
    """
    listInstanceInfo = []
    response = ec2client.describe_instances(Filters=custom_filter)

    if response == []:
        print('No instances.')
    else:
        for x2 in response['Reservations']:
            for x3 in x2['Instances']:
                instanceInfo = {}
                instanceInfo['Id'] = x3['InstanceId']
                instanceInfo['State'] = x3['State']['Name']
                if x3['State']['Name'] != 'terminated':
                    instanceInfo['VpcId'] = x3['VpcId']
                else:
                    instanceInfo['VpcId'] = ''
                listInstanceInfo.append(instanceInfo)

    return listInstanceInfo

def listVpc():
    """
    return a list of VPC 
    """
    listVpcInfo = []
    vpcs = ec2client.describe_vpcs(Filters=custom_filter)
    for x2 in vpcs['Vpcs']:
        vpcInfo = {}
        vpcInfo['Id'] = x2['VpcId']
        vpcInfo['State'] = x2['State']
        listVpcInfo.append(vpcInfo)

    return listVpcInfo


def listSg():
    """
    return a list of security groups with properties ID, VPC ID, IngressRules, EgressRule
    """
    listSgInfo = []
    sgs = ec2client.describe_security_groups(Filters=custom_filter)
    for x2 in sgs['SecurityGroups']:
        sgInfo = {}
        sgInfo['GroupName'] = x2['GroupName']
        sgInfo['Id'] = x2['GroupId']
        sgInfo['VpcId'] = x2['VpcId']
        sgInfoIngressSecGroup = []
        sgInfoEgressSecGroup = []
        x3 = x2['IpPermissions']
        for x4 in x3:
            for x5 in x4['UserIdGroupPairs']:
                sgInfoIngressSecGroup.append(x5['GroupId'])
        sgInfo['IngressSecGroup'] = sgInfoIngressSecGroup

        y3 = x2['IpPermissionsEgress']
        for y4 in y3:
            for y5 in y4['UserIdGroupPairs']:
                sgInfoEgressSecGroup.append(y5['GroupId'])
        sgInfo['EgressSecGroup'] = sgInfoEgressSecGroup

        listSgInfo.append(sgInfo)

    return listSgInfo


def listSgRules(sgId):
    """
    return list of ingress rule list and egress rules list of a security group
    """
    ingressRules = []
    egressRules = []
    newfilter = [
        {
            'Name': 'group-id',
            'Values': [str(sgId)]
        }
    ]
    response = ec2client.describe_security_group_rules(Filters=newfilter)

    sgRules = response['SecurityGroupRules']
    for sgRule in sgRules:
        if sgRule['IsEgress']:
            egressRules.append(sgRule['SecurityGroupRuleId'])
        else:
            ingressRules.append(sgRule['SecurityGroupRuleId'])

    return ingressRules, egressRules

def listRuleSource(ruleId):
    newfilter = [
        {
            'Name': 'security-group-rule-id',
            'Values': [ruleId]
        }
    ]
    response = ec2client.describe_security_group_rules(Filters=newfilter)
    if 'SecurityGroupRules' in response and response['SecurityGroupRules']:
        rule = response['SecurityGroupRules'][0]
        #print(f"Rule ID: {rule['SecurityGroupRuleId']}")
        #print(f"Source: {rule.get('CidrIpv4', 'N/A')}")
        if rule.get('CidrIpv4', 'N/A') == '0.0.0.0/0':
            return True
    
    else:
        #print(f"Rule with ID {ruleId} not found.")
        return False

def listRuleDestination(ruleId):
    newfilter = [
        {
            'Name': 'security-group-rule-id',
            'Values': [ruleId]
        }
    ]
    response = ec2client.describe_security_group_rules(Filters=newfilter)
    if 'SecurityGroupRules' in response and response['SecurityGroupRules']:
        rule = response['SecurityGroupRules'][0]
        #print(f"Rule ID: {rule['SecurityGroupRuleId']}")
        #print(f"Destination: {rule.get('CidrIpv4', 'N/A')}")
        if rule.get('CidrIpv4', 'N/A') == '0.0.0.0/0':
            return True
    else:
        #print(f"Rule with ID {ruleId} not found.")
        return False

def insecureRules(sgId):
    ingressRules, egressRules = listSgRules(sgId)
    for ingressRule in ingressRules:
        if listRuleSource(ingressRule):
            print(f"Security Group {sgId} --> Insecure ingress rule: {ingressRule}")
    for egressRule in egressRules:
        if listRuleDestination(egressRule):
            print(f"Security Group {sgId} --> Insecure egress rule: {egressRule}")


def minusLine():
    print("-------------------------------------------------------------------------------------------------------")


def main():
    # progressive bar
    aliveBar(10, 0.05, 'Displaying current inventory status...')
    separator()
    # Display Instances info
    listInstanceInfo = listInstance()
    listInstanceId = []
    listSgInfo = listSg()
    print("Insecure ingress and egress rules:")
    for sg in listSgInfo:
        sgId = sg['Id']
        insecureRules(sgId)
    separator()
    print("Instances on the account:")
    if not listInstanceInfo:
        print("There is no instance.")
    for instance in listInstanceInfo:
        print(instance['Id'], '-->', 'in VPC',
              instance['VpcId'], '--> State', instance['State'])

    if listInstanceInfo:
        listInstanceState = []
        for instance in listInstanceInfo:
            listInstanceState.append(instance['State'])
            if instance['State'] not in ['terminated', 'terminating']:
                listInstanceId.append(instance['Id'])
            if all(element == 'terminated' for element in listInstanceState):
                terminatedFlag = False
            else:
                terminatedFlag = True
    else:
        print('All instances are gone! or no more instances.')
        terminatedFlag = False

    # Display VPC info
    separator()
    listVpcInfo = listVpc()
    listVpcId = []
    for vpcInfo in listVpcInfo:
        listVpcId.append(vpcInfo['Id'])
        print(vpcInfo['Id'], '-->', 'State', vpcInfo['State'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Script to remove insecure rules where source or destination is 0.0.0.0/0', 
        usage="python3 sgfix.py profile_name region_name",
        epilog='To run the script: python3 sgfix.py profile_name region_name')
    parser.add_argument('profile_name', help='AWS profile name')
    parser.add_argument('region_name', help='AWS region name')
    args = parser.parse_args()

    # Initialize AWS clients
    initialize_clients(args.profile_name, args.region_name)

    # Call the main function
    main()