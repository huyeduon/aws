#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Huyen Duong, huyeduon@cisco.com, TME CNBU.
# Quality: POC
# Requirements: python3, boto3, aws cli
# changes
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

def listInfraEc2():
    # return a list of instanceId by filtering all instance who has tag key owner, tag value huyen
    infraEc2 = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }

    ]
    ecs = ec2client.describe_instances(Filters=custom_filter)
    for x2 in ecs['Reservations']:
        for x3 in x2['Instances']:
            instanceId = x3['InstanceId']
            infraEc2.append(instanceId)

    return infraEc2

def listSubnet():
    # return a list of subnet ID
    subnetIds = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    subnets = ec2client.describe_subnets(Filters=custom_filter)
    for x2 in subnets['Subnets']:
        subnetIds.append(x2['SubnetId'])
    
    return subnetIds

def listSg():
    sgIds = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    sgs = ec2client.describe_security_groups(Filters=custom_filter)
    for x2 in sgs['SecurityGroups']:
        sgIds.append(x2['GroupId'])
    
    return sgIds

def listRt():
    rtIds = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    rts = ec2client.describe_route_tables(Filters=custom_filter)
    for x2 in rts['RouteTables']:
        rtIds.append(x2['RouteTableId'])
    
    return rtIds

def listIgw():
    igwIds = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    igws = ec2client.describe_internet_gateways(Filters=custom_filter)
    for x2 in igws['InternetGateways']:
        igwIds.append(x2['InternetGatewayId'])
    return igwIds

def listVpc():
    vpcIds = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    vpcs = ec2client.describe_vpcs(Filters=custom_filter)
    for x2 in vpcs['Vpcs']:
        vpcIds.append(x2['VpcId'])
    return vpcIds

def listTgw():
    # return a list of TGW has tag key=owner, value=huyen
    listTgwId = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }

    ]
    tgw = ec2client.describe_transit_gateways(Filters=custom_filter)
    for x2 in tgw['TransitGateways']:
        listTgwId.append(x2['TransitGatewayId'])

    return listTgwId

def listTgwRt():
    # return list of TGW Route Table ID who has tag key=owner, value=huyen
    listTgwRtId = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }

    ]
    tgwRt = ec2client.describe_transit_gateway_route_tables(
        Filters=custom_filter)
    x2 = tgwRt['TransitGatewayRouteTables']
    for x3 in x2:
        listTgwRtId.append(x3['TransitGatewayRouteTableId'])

    return listTgwRtId

def delTgwVpcAttachment(attachmentId):
    try:
        ec2client.delete_transit_gateway_vpc_attachment(TransitGatewayAttachmentId=attachmentId)
    except ClientError:
        logger.exception("Could not delete TGW VPC attachment!")
        raise
    else:
        return response

def checkAttachmentExistence():
    # return number of attachment and list of attachment ID
    attachmentInfoList = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    tgw = ec2client.describe_transit_gateway_vpc_attachments(
        Filters=custom_filter)
    # x2 is list of attachment
    x2 = tgw['TransitGatewayVpcAttachments']
    numOfAttachment = len(x2)
    for x3 in x2:
        attachmentInfo = {}
        attachmentInfo['TransitGatewayAttachmentId'] = x3['TransitGatewayAttachmentId']
        attachmentInfo['State'] = x3['State']
        attachmentInfoList.append(attachmentInfo)

    return numOfAttachment, attachmentInfoList

def tgwRtDeletionEligibility():
    # check if all tunnel are in deleted state, return true, else return false
    eligibleDeletion = True
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    tgw = ec2client.describe_transit_gateway_vpc_attachments(
        Filters=custom_filter)
    x2 = tgw['TransitGatewayVpcAttachments']
    for x3 in x2:
        if x3['State'] != 'deleted':
            eligibleDeletion = False
    return eligibleDeletion

def defaultAssociationStateCheck():
    # return default route table association state "enable" or "disable"
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    tgw = ec2client.describe_transit_gateways(Filters=custom_filter)
    for x2 in tgw['TransitGateways']:
        defaultAssociationState = x2['Options']['DefaultRouteTableAssociation']
    return defaultAssociationState

def disableDefaultAssociationAndPropagation(tgwId):
    ec2client.modify_transit_gateway(TransitGatewayId=tgwId, Options={
        'DefaultRouteTableAssociation': 'disable',
        'DefaultRouteTablePropagation': 'disable' 
        }
    )

def delTgwRouteTable(tgwRouteTableId):
    # delete TGW Route Table
    while True:
        time.sleep(30)
        numOfAttachment, attachmentInfoList = checkAttachmentExistence()
        defaultAssociationState = defaultAssociationStateCheck()
        if defaultAssociationState == 'enable':
            print('Disable default route association...')
            Tgws = listTgw()
            for tgw in Tgws:
                disableDefaultAssociationAndPropagation(tgw)
        # if still have attachment and exist at least one attachment not in Deleted state
        if numOfAttachment != 0 and not tgwRtDeletionEligibility():
            print('Deleting VPC Attachment...')
            print('Be patient...')
            for attachment in attachmentInfoList:
                print(attachment)
                if attachment['State'] != 'deleted':
                    delTgwVpcAttachment(attachment['TransitGatewayAttachmentId'])
        elif tgwRtDeletionEligibility():
            try:
                ec2client.delete_transit_gateway_route_table(
                    TransitGatewayRouteTableId=tgwRouteTableId)
            except ClientError:
                logger.exception("Could not delete TGW Route table!")
                raise
            else:
                return response

def delTgw(tgw):
   ec2client.delete_transit_gateway(TransitGatewayId=tgw)

def checkInstanceExistence():
    # return number of attachment and list of attachment ID
    instanceInfoList = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    x1 = ec2client.describe_instances(Filters=custom_filter)
    numOfInstance = len(x1['Reservations'])
    # x2 is a list
    for x2 in x1['Reservations']:
        for x3 in x2['Instances']:
            instanceInfo = {}
            instanceId = x3['InstanceId']
            instanceState = x3['State']['Name']
            instanceInfo['InstanceId'] = instanceId
            instanceInfo['State'] = instanceState
            instanceInfoList.append(instanceInfo)

    return numOfInstance, instanceInfoList

def subnetDeletionEligibility():
    # check if all instances are in terminated state, return true, else return false
    eligibleDeletion = True
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    x1 = ec2client.describe_instances(Filters=custom_filter)
    for x2 in x1['Reservations']:
        for x3 in x2['Instances']:
            instanceState = x3['State']['Name']
            if instanceState != 'terminated':
                eligibleDeletion = False
    return eligibleDeletion

def delInstance(vms):
    #vms is list of instances
    ec2client.terminate_instances(InstanceIds=vms)

# Delete subnet
def delSubnet(subnet):
    # delete subnet
    while True:
        time.sleep(30)
        numOfInstance, instanceInfoList = checkInstanceExistence()
        # if still have non-terminated state instances, terminate those instances
        if numOfInstance != 0 and not subnetDeletionEligibility():
            print('Terminating Instances...')
            print('Be patient...')
            for instance in instanceInfoList:
                instanceIdList = []
                if instance['State'] != 'terminated':
                    instanceIdList.append(instance['InstanceId'])
                    delInstance(instanceIdList)
        # if all instances are in terminated state then subnets can be deleted
        elif subnetDeletionEligibility():
            try:
                ec2client.delete_subnet(SubnetId=subnet)
            except ClientError:
                logger.exception("Could not delete TGW Route table!")
                raise
            else:
                return response

def delRt(rt):
    # rt is string
    ec2client.delete_route_table(RouteTableId=rt)

def delSg(sg):
    #sg is string
    ec2client.delete_security_group(GroupId=sg)

# detach all InternetGateway
def detachIgw(igw, vpcid):
    # igw is strings
    ec2client.detach_internet_gateway(InternetGatewayId=igw, VpcId=vpcid)

def checkIgwExistence():
    # return number of attachment and list of attachment ID
    igwInfoList = []
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    x1 = ec2client.describe_internet_gateways(Filters=custom_filter)
    # x2 is a list
    x2 = x1['InternetGateways']
    numOfIgw = len(x2)
    if numOfIgw == 0:
        igwInfoList = []
    else:
        for x3 in x2:
            igwInfo = {}
            igwInfo['InternetGatewayId'] = x3['InternetGatewayId']
            if len(x3['Attachments']) != 0:
                igwInfo['State'] = 'available'
                igwInfo['VpcId'] = x3['Attachments'][0]['VpcId']
            else:
                igwInfo['State'] = 'NA'
                igwInfo['VpcId'] = 'NA'
            igwInfoList.append(igwInfo)
    return numOfIgw, igwInfoList

def igwDeletionEligibility():
    # check if IGW can be deleted or not. if state is detached it can be deleted.
    eligibleDeletion = True
    custom_filter = [
        {
            'Name': 'tag:owner',
            'Values': ['huyen']
        }
    ]
    x1 = ec2client.describe_internet_gateways(Filters=custom_filter)
    x2 = x1['InternetGateways']
    if len(x2) == 0:
        eligibleDeletion = True
    else:
        for x3 in x2:
            x4 = len(x3['Attachments'])
            if x4 == 0:
                eligibleDeletion = True
            elif x4 > 0:
                if x3['Attachments'][0]['State'] == "available":
                    eligibleDeletion = False
                else:
                    eligibleDeletion = True
    return eligibleDeletion

# delete Internet Gateway
def delIgw(igw):
    # igw is string
    while True:
        time.sleep(3)
        numOfIgw, igwInfoList = checkIgwExistence()

        # if still have IGW and IGW is not detached
        if numOfIgw == 0:
            break
        if numOfIgw != 0 and not igwDeletionEligibility():
            print('Detaching Internet Gateways...')
            for igw in igwInfoList:
                if igw['State'] == 'available':
                   detachIgw(igw['InternetGatewayId'],igw['VpcId'])
        # if all igw are detached.
        elif igwDeletionEligibility():
            for igw in igwInfoList:
                igwId = igw['InternetGatewayId']
                ec2client.delete_internet_gateway(InternetGatewayId=igwId)

# delete VPC
def delVpc(vpc):
    #vpc is string
    ec2client.delete_vpc(VpcId=vpc)
   
def main():
    print("Deleting TGW Route Table")
    tgwRtIds = listTgwRt()
    for tgwRtId in tgwRtIds:
        delTgwRouteTable(tgwRtId)
    print("TGW Route Table deletion completed.")
    print("=========******====================")

    print("Deleting TGW")
    tgwIds = listTgw()
    for tgwId in tgwIds:
        delTgw(tgwId)
    print("TGW deletion completed.")

    print("=========******====================")
    print("=========******====================")
    print("=========******====================")

    # inventory 
    print("Inventory...")

    inst = listInfraEc2()
    subnets = listSubnet()
    sgs = listSg()
    rts = listRt()
    igws = listIgw()
    vpcs = listVpc()

    print("Instances: ", inst)
    print("Subnets: ", subnets)
    print("Security Groups: ", sgs)
    print("Route Tables: ", rts)
    print("Internet Gateway: ", igws)
    print("VPC: ", vpcs)
    
    print("Starting decomissioning EC2 instances and  networks...")

    if len(inst) != 0:
        print("Terminating instances...")
        delInstance(inst)

    if len(subnets) != 0:
        print("Deleting subnets...")
        for subnet in subnets:
            delSubnet(subnet)
    if len(sgs) != 0:
        print("Deleting Security Groups...")
        for sg in sgs:
            delSg(sg)
    if len(rts) != 0:
        print("Deleting Route Tables...")
        for rt in rts:
            delRt(rt)
    
    if len(igws) != 0:
        print("Deleting IGW...")
        for igw in igws:
            delIgw(igw)

    if len(vpcs) != 0:
        print("Deleting VPC:")
        for vpc in vpcs:
            delVpc(vpc)

    print("Congratulations, all resources have been decomissioned successfully!")
 
if __name__ == "__main__":
    main()