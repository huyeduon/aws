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
import boto3
import sys
from botocore.config import Config
import time

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

custom_filter = [
    {
        'Name': 'tag:owner',
        'Values': ['huyen']
    }

]

def listInstance():
    # return a list of TGW has tag key=owner, value=huyen
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
    listVpcInfo = []
    vpcs = ec2client.describe_vpcs(Filters=custom_filter)
    for x2 in vpcs['Vpcs']:
        vpcInfo = {}
        vpcInfo['Id'] = x2['VpcId']
        vpcInfo['State'] = x2['State']
        listVpcInfo.append(vpcInfo)
    return listVpcInfo

def listSubnet():
    # return a list of subnet ID
    listSubnetInfo = []
 
    subnets = ec2client.describe_subnets(Filters=custom_filter)
    for x2 in subnets['Subnets']:
        subnetInfo = {}
        subnetInfo['Id'] = x2['SubnetId']
        subnetInfo['VpcId'] = x2['VpcId']
        subnetInfo['State'] = x2['State']
        listSubnetInfo.append(subnetInfo)

    return listSubnetInfo

def listSg():
    listSgInfo = []
    sgs = ec2client.describe_security_groups(Filters=custom_filter)
    for x2 in sgs['SecurityGroups']:
        sgInfo= {}
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

# list all ingress rules and egress rules of a specific SG
def listSgRules(sgId):
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


def listRt():
 
    listRtInfo = []
    
    rts = ec2client.describe_route_tables(Filters=custom_filter)
    for x2 in rts['RouteTables']:
        rtInfo = {}
        rtInfo['Id'] = x2['RouteTableId']
        rtInfo['VpcId'] = x2['VpcId']
        listRtInfo.append(rtInfo)

    return listRtInfo

def listIgw():
    listIgwInfo = []
    igws = ec2client.describe_internet_gateways(Filters=custom_filter)
    for x2 in igws['InternetGateways']:
        igwInfo = {}
        igwInfo['Id'] = x2['InternetGatewayId']
        igwInfo['State'] = x2['Attachments'][0]['State']
        igwInfo['VpcId'] = x2['Attachments'][0]['VpcId']
        listIgwInfo.append(igwInfo)
    
    return listIgwInfo

def terminateInstance(listInstanceId):
    ec2client.terminate_instances(InstanceIds=listInstanceId)

def instanceTerminated(vpcId):
    # check state of all instance in a VPC with ID: vpcId
    eligibleDeletion = False
    newfilter = [
        {
            'Name': 'vpc-id',
            'Values': [str(vpcId)]
        }
    ]
    while not eligibleDeletion:
        response = ec2client.describe_instances(Filters=newfilter)
        listInstanceState = []
    
        if response['Reservations'] == []:
            eligibleDeletion = True
        else:
            for instances in response['Reservations']:
                for instance in instances['Instances']:
                    listInstanceState.append(instance['State']['Name'])
            if all(element == 'terminated' for element in listInstanceState):
                eligibleDeletion = True
            else:
                eligibleDeletion = False
    return eligibleDeletion

def delIgw(igwId):
    ec2client.delete_internet_gateway(InternetGatewayId=igwId)

def detachIgw(igwId, vpcId):
    ec2client.detach_internet_gateway(InternetGatewayId=igwId, VpcId=vpcId)

def delRt(rtId):
    ec2client.delete_route_table(RouteTableId=rtId)

def delSubnet(subnetId):
    ec2client.delete_subnet(SubnetId=subnetId)

def delSg(sgId):
    ec2client.delete_security_group(GroupId=sgId)

def delInSgRules():
    ec2client.revoke_ingress()

def delEgSgRules():
    ec2client.revoke_egress()

def delVpc(vpcId):
    eligibleDeletion = False
    instancefilter = [
        {
            'Name': 'vpc-id',
            'Values': [str(vpcId)]
        }
    ]
    while not eligibleDeletion:
        response = ec2client.describe_instances(Filters=instancefilter)
        listInstanceState = []

        if response['Reservations'] == []:
            eligibleDeletion = True
        else:
            for instances in response['Reservations']:
                for instance in instances['Instances']:
                    listInstanceState.append(instance['State']['Name'])
            if all(element == 'terminated' for element in listInstanceState):
                eligibleDeletion = True
            else:
                eligibleDeletion = False

    if eligibleDeletion:
        #1 detach IGW 
        #2 delete Route Tables except Main Route Table
        listIgwId = []
        igwfilter = [
            {
                'Name': 'attachment.vpc-id',
                'Values': [str(vpcId)]
            }
        ]
        igws = ec2client.describe_internet_gateways(Filters=igwfilter)

        # detach IGW
        for igw in igws['InternetGateways']:
            if igw['Attachments'][0]['State'] not in ['detached', 'detaching']:
                listIgwId.append(igw['InternetGatewayId'])
                detachIgw(igw['InternetGatewayId'], vpcId)
                time.sleep(10)

        # delete IGW
        for igwId in listIgwId:
            delIgw(igwId)
            time.sleep(10)

        # check Route Tables
        listRtId = []
        associatedSubnetId = []
        rtfilter = [
            {
                'Name': 'vpc-id',
                'Values': [str(vpcId)]
            }
        ]
        rtsResponse = ec2client.describe_route_tables(Filters=rtfilter)
        rts = rtsResponse['RouteTables']
        for rt in rts:
            rtAssocations = rt['Associations']
            for rtAssociation in rtAssocations:
                if rtAssociation['Main'] == False:
                    listRtId.append(rt['RouteTableId'])
                    associatedSubnetId.append(rtAssociation['SubnetId'])

        # delete all associated Subnets
        for associateSubnet in associatedSubnetId:
            delSubnet(associateSubnet)
            time.sleep(5)

        # delete route tables
        for rtId in listRtId:
            delRt(rtId)
            time.sleep(5)
        
        # list all security group in VPC
        sgfilter = [
            {
                'Name': 'vpc-id',
                'Values': [str(vpcId)]
            }
        ]
        sgResponse = ec2client.describe_security_groups(Filters=sgfilter)
        listSgInfo = []
        for x2 in sgResponse['SecurityGroups']:
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

        # delete security group rules
        for sgInfo in listSgInfo:
            ingressRules, egressRules = listSgRules(sgInfo['Id'])
            if ingressRules:
                for ingressRule in ingressRules:
                    print('Deleting ingress rules...', ingressRule)
                ec2client.revoke_security_group_ingress(GroupId=sgInfo['Id'], SecurityGroupRuleIds=ingressRules)
                time.sleep(5)
            if egressRules:
                for egressRule in egressRules:
                    print('Deleting egress rules...', egressRule)
                ec2client.revoke_security_group_egress(GroupId=sgInfo['Id'], SecurityGroupRuleIds=egressRules)
                time.sleep(5)

        # delete security groups...
        for sgInfo in listSgInfo:
            if sgInfo['GroupName'] != 'default':
                print('Deleting Security Group', sgInfo['Id'])
                delSg(sgInfo['Id'])
                time.sleep(2)

        time.sleep(45)
        ec2client.delete_vpc(VpcId=vpcId)

def separator():
    print("================================================")

def minusLine():
    print("------------------------------------------------")

def main():
    print('Inventory.....')
    minusLine()
    # Display Instances info
    listInstanceInfo = listInstance()
    terminatedFlag = False
    listInstanceId = []
    print("Instances on the account:")
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
        print('All instances are gone!')
        terminatedFlag = False

    # Display Security Groups info
    separator()
    separator()
    print("Security Groups:")
    listSgInfo = listSg()
    for sgInfo in listSgInfo:
        print('Security Group Name:', sgInfo['GroupName'], '|', sgInfo['Id'], sgInfo['VpcId'], '|', 'IngressRuleGroup:',
              sgInfo['IngressSecGroup'],'|','EgressRuleGroup:', sgInfo['EgressSecGroup'])
    
    # Display Internet Gateways info
    separator()
    separator()
    print("Internet Gateway current information:")
    listIgwInfo = listIgw()
    for igwInfo in listIgwInfo:
        print(igwInfo['Id'], '-->' ,'State',igwInfo['State'], '-->', igwInfo['VpcId'])
    
    # Display VPC info
    separator()
    separator()
    listVpcInfo = listVpc()
    listVpcId = []
    for vpcInfo in listVpcInfo:
        listVpcId.append(vpcInfo['Id'])
        print(vpcInfo['Id'],'-->' , 'State', vpcInfo['State'])

    # Decomissioning process
    separator()
    separator()
    print('Start decomissioning process...')
    print('Terminate Instances and then terminate VPC.')
    print('This process is destructive!!!')
    print('--> Start terminating instances...')
    # terminate instances
    if terminatedFlag:
        for i in range(len(listInstanceId)):
            singleInstance = []
            singleInstance.append(listInstanceId[i])
            print('Terminating instance', singleInstance)
            terminateInstance(singleInstance)
    minusLine()
    print('--> Start deleting VPC...')
    for vpcId in listVpcId:
        print('Deleting VPC', vpcId)
        delVpc(vpcId)
    print('All VPCs are gone !!! Good bye !!!')

if __name__ == "__main__":
    main()
