#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from botocore.config import Config
import re
import boto3
import sys
import time
from alive_progress import alive_bar

profileName = "htduong06"
regionName = "eu-south-1"

htduong06 = Config(
    region_name=regionName,
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)


session = boto3.session.Session(profile_name="htduong06")
ec2client = session.client('ec2', config=htduong06)
cftclient = session.client('cloudformation', config=htduong06)
resourcesclient = session.client('resource-groups', config=htduong06)

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

    for eip in eips:
        eipInfo = {}
        eipInfo['PublicIp'] = eip['PublicIp']
        eipInfo['AllocationId'] = eip['AllocationId']
        if 'AssociationId' in eip:
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


def disAssociateEip(AssociationId):
    """
    dis-associate EIP from instances
    """
    ec2client.disassociate_address(AssociationId=AssociationId)


def releaseEip(AllocationId):
    """
    release EIP
    """
    ec2client.release_address(AllocationId=AllocationId)


def listcApicInfraEni():
    """
    return a cAPIC Infra ENI
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


def listcApicOobEni():
    """
    return a cAPIC OOB ENI
    """
    capicEni_filter = [
        {
            'Name': 'tag:aws:cloudformation:logical-id',
            'Values': ['rCAPICOOBInterface']
        }
    ]

    listcApicEni = []

    response = ec2client.describe_network_interfaces(
        Filters=capicEni_filter)
    capicEni = response['NetworkInterfaces']
    for eni in capicEni:
        listcApicEni.append(eni['NetworkInterfaceId'])

    return listcApicEni


def delEni(eni):
    ec2client.delete_network_interface(NetworkInterfaceId=eni)


def listTgw():
    """
    return a list of TGW that has tag key=owner, value=huyen
    """
    listTgwInfo = []
    tgw = ec2client.describe_transit_gateways(Filters=custom_filter)
    for x2 in tgw['TransitGateways']:
        tgwInfo = {}
        tgwInfo['Id'] = x2['TransitGatewayId']
        tgwInfo['State'] = x2['State']
        listTgwInfo.append(tgwInfo)

    return listTgwInfo


def listTgwVpcAttachment(tgwId):
    """
    return a list of VPC attachment of Transit Gateway whose ID is tgwId
    """
    newfilter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgwId)]
        }
    ]
    listTgwVpcAttachmentInfo = []
    tgwVpcAttachmentId = ec2client.describe_transit_gateway_vpc_attachments(
        Filters=newfilter)

    for x2 in tgwVpcAttachmentId['TransitGatewayVpcAttachments']:
        tgwVpcAttachmentInfo = {}
        tgwVpcAttachmentInfo['Id'] = x2['TransitGatewayAttachmentId']
        tgwVpcAttachmentInfo['State'] = x2['State']
        tgwVpcAttachmentInfo['VpcId'] = x2['VpcId']
        listTgwVpcAttachmentInfo.append(tgwVpcAttachmentInfo)

    return listTgwVpcAttachmentInfo


def listTgwConnect(tgwId):
    """
    return a list of TGW Connect Attachment of Transit Gateway whose ID is tgwId
    """
    newfilter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgwId)]
        }
    ]
    listTgwConnectInfo = []
    tgwConnectId = ec2client.describe_transit_gateway_connects(
        Filters=newfilter)
    for tgwConnect in tgwConnectId['TransitGatewayConnects']:
        tgwConnectInfo = {}
        tgwConnectInfo['Id'] = tgwConnect['TransitGatewayAttachmentId']
        tgwConnectInfo['State'] = tgwConnect['State']
        listTgwConnectInfo.append(tgwConnectInfo)

    return listTgwConnectInfo


def listTgwConnectPeer(tgwConnectAttachId):
    """
    return a list of TGW connect peer of TGW Connect whose ID is tgwConnectAttachId
    """
    listTgwConnectPeerInfo = []
    newfilter = [
        {
            'Name': 'transit-gateway-attachment-id',
            'Values': [str(tgwConnectAttachId)]
        }
    ]
    tgwConnectPeerId = ec2client.describe_transit_gateway_connect_peers(
        Filters=newfilter)

    for x2 in tgwConnectPeerId['TransitGatewayConnectPeers']:
        tgwConnectPeerInfo = {}
        tgwConnectPeerInfo['Id'] = x2['TransitGatewayConnectPeerId']
        tgwConnectPeerInfo['State'] = x2['State']
        listTgwConnectPeerInfo.append(tgwConnectPeerInfo)

    return listTgwConnectPeerInfo


def listTgwPeering(tgwId):
    """
    return a list of TGW Peering Attachment of Transit Gateway whose ID is tgwId
    """
    newfilter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgwId)]
        }
    ]
    listTgwPeeringInfo = []
    response = ec2client.describe_transit_gateway_peering_attachments(
        Filters=newfilter)
    tgwPeeringAttachments = response['TransitGatewayPeeringAttachments']
    for twgPeeringAttachment in tgwPeeringAttachments:
        tgwPeeringInfo = {}
        tgwPeeringInfo['Id'] = twgPeeringAttachment['TransitGatewayAttachmentId']
        tgwPeeringInfo['State'] = twgPeeringAttachment['State']
        listTgwPeeringInfo.append(tgwPeeringInfo)

    return listTgwPeeringInfo


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


def listSubnet():
    """ 
    return a list of subnet ID each has properties: ID, VPC ID and State
    """
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


def listRt():
    """
    return a list of route table with properties of RouteTableId, VPC ID
    """
    listRtInfo = []

    rts = ec2client.describe_route_tables(Filters=custom_filter)
    for x2 in rts['RouteTables']:
        rtInfo = {}
        rtInfo['Id'] = x2['RouteTableId']
        rtInfo['VpcId'] = x2['VpcId']
        listRtInfo.append(rtInfo)

    return listRtInfo


def listIgw():
    """
    return a list of Internet Gateways with properties State and VPC ID
    """
    listIgwInfo = []
    igws = ec2client.describe_internet_gateways(Filters=custom_filter)
    for x2 in igws['InternetGateways']:
        igwInfo = {}
        if x2['Attachments']:
            igwInfo['Id'] = x2['InternetGatewayId']

            igwInfo['State'] = x2['Attachments'][0]['State']
            igwInfo['VpcId'] = x2['Attachments'][0]['VpcId']
            listIgwInfo.append(igwInfo)
        else:
            print('Internet Gateway is detached.')

    return listIgwInfo


def delTgwPeering(tgwPeeringId):
    ec2client.delete_transit_gateway_peering_attachment(
        TransitGatewayAttachmentId=tgwPeeringId)


def delTgwConnectPeer(connectPeerId):
    """
    delete tgw connnect peers of tgw connect attachment whose ID is connectPeerId
    """
    ec2client.delete_transit_gateway_connect_peer(
        TransitGatewayConnectPeerId=connectPeerId)


def delTgwConnect(connectAttachmentId):
    """
    check if it is possible to delete tgwConnect attachment
    only delete tgwConnect attachment if all connectPeers are in deleted state
    """
    eligibleDeletion = False

    listTgwConnectPeerInfo = listTgwConnectPeer(connectAttachmentId)
    eligibleConnectPeers = []
    # delete all connect peers who are not in deleted or deleting state.
    for tgwConnectPeerInfo in listTgwConnectPeerInfo:
        if tgwConnectPeerInfo['State'] not in ['deleted', 'deleting']:
            #print("Deleting TGW Connect Peer", tgwConnectPeerInfo['Id'], "in", connectAttachmentId)
            delTgwConnectPeer(tgwConnectPeerInfo['Id'])
            eligibleConnectPeers.append(tgwConnectPeerInfo['Id'])

    # progressive bar
    for eligibleConnectPeer in eligibleConnectPeers:
        aliveBar(1500 + randrange(100, 200), 0.05,
                 "Deleting Connect Peer " + eligibleConnectPeer)

    # check if all connect peer are in delete states
    while not eligibleDeletion:
        time.sleep(30)
        listState = []
        listTgwConnectPeerInfo = listTgwConnectPeer(connectAttachmentId)

        for tgwConnectPeerInfo in listTgwConnectPeerInfo:
            listState.append(tgwConnectPeerInfo['State'])

        if listTgwConnectPeerInfo == []:
            eligibleDeletion = True
        else:
            if all(element == 'deleted' for element in listState):
                eligibleDeletion = True
                print(
                    "All peers in deleted state, start deleting TGW Connect Attachment...")

    print("Deleting TGW Connect Attachment ", connectAttachmentId)

    if eligibleDeletion:
        ec2client.delete_transit_gateway_connect(
            TransitGatewayAttachmentId=connectAttachmentId)


def delTgwVpcAttachment(tgwVpcAttachmentId):
    """
    find all tgwConnectAttachment who use that vpc as transport attachmentInfoList
    if tgwConnectAttachment state is deleted then delete VPC attachment
    """
    eligibleDeletion = False

    newfilter = [
        {
            'Name': 'transport-transit-gateway-attachment-id',
            'Values': [str(tgwVpcAttachmentId)]
        }
    ]

    while not eligibleDeletion:
        time.sleep(15)
        listConnectState = []
        response = ec2client.describe_transit_gateway_connects(
            Filters=newfilter)

        if response == []:
            eligibleDeletion = True
        else:
            tgwConnectAttachments = response['TransitGatewayConnects']
            for tgwConnectAttachment in tgwConnectAttachments:
                listConnectState.append(tgwConnectAttachment['State'])
            if all(element == 'deleted' for element in listConnectState):
                eligibleDeletion = True
                print(
                    "All Connect Attachments are in deleted state, start deleting VPC Attachment...")

    #print("Deleting TGW VPC Attachment", tgwVpcAttachmentId)

    if eligibleDeletion:
        ec2client.delete_transit_gateway_vpc_attachment(
            TransitGatewayAttachmentId=tgwVpcAttachmentId)


def delTgw(tgwId):
    """
    delete Transit Gateway whose ID is tgwId
    """
    eligibleDeletion = False
    tgw_filter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgwId)]
        }
    ]

    while not eligibleDeletion:
        time.sleep(45)
        response = ec2client.describe_transit_gateway_attachments(
            Filters=tgw_filter)

        if response == []:
            eligibleDeletion = True
        else:
            tgwAttachments = response['TransitGatewayAttachments']
            listAttachmentState = []
            for tgwAttachment in tgwAttachments:
                listAttachmentState.append(tgwAttachment['State'])
            if all(element == 'deleted' for element in listAttachmentState):
                eligibleDeletion = True
                print("All TGW Attachments are in deleted state.")
    print('Deleting TGW...')
    if eligibleDeletion:
        ec2client.delete_transit_gateway(TransitGatewayId=tgwId)


def terminateInstance(listInstanceId):
    """
    terminate instances whose ID are in in the list listInstanceId
    """
    ec2client.terminate_instances(InstanceIds=listInstanceId)


def instanceTerminated(vpcId):
    """
    check state of all instance in a VPC with ID: vpcId
    return eligible deletion status, if status is True means all instances are gone or deleted we can proceed
    """
    eligibleDeletion = False
    instance_filter = [
        {
            'Name': 'vpc-id',
            'Values': [str(vpcId)]
        }
    ]
    while not eligibleDeletion:
        response = ec2client.describe_instances(Filters=instance_filter)
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
    """
    delete Internet Gateway with ID igwId
    """
    ec2client.delete_internet_gateway(InternetGatewayId=igwId)


def detachIgw(igwId, vpcId):
    """
    detach Internet Gateway igwId out of VPC vpcId
    """
    ec2client.detach_internet_gateway(InternetGatewayId=igwId, VpcId=vpcId)


def delRt(rtId):
    """
    delete Route Table with ID rtId
    """
    ec2client.delete_route_table(RouteTableId=rtId)


def delSubnet(subnetId):
    """
    delete subnet with ID subnetId
    """
    ec2client.delete_subnet(SubnetId=subnetId)


def delSg(sgId):
    """
    delete security group with ID sgId
    """
    ec2client.delete_security_group(GroupId=sgId)


def delInSgRules():
    """
    delete all ingress security rules
    """
    ec2client.revoke_ingress()


def delEgSgRules():
    """
    delete all egress security rules
    """
    ec2client.revoke_egress()


def delVpc(vpcId):
    """
    delete VPC whose ID is vpcId
    """
    eligibleDeletion = False
    instance_filter = [
        {
            'Name': 'vpc-id',
            'Values': [str(vpcId)]
        }
    ]
    while not eligibleDeletion:
        response = ec2client.describe_instances(Filters=instance_filter)
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

        # delete all subnets in the VPC
        subnet_filter = [
            {
                'Name': 'vpc-id',
                'Values': [str(vpcId)]
            }
        ]
        subnetResponse = ec2client.describe_subnets(Filters=subnet_filter)
        subnets = subnetResponse['Subnets']
        listSubnetId = []

        for subnet in subnets:
            listSubnetId.append(subnet['SubnetId'])

        print('Deleting subnets...')
        for subnetId in listSubnetId:
            delSubnet(subnetId)
            time.sleep(5)
            aliveBar(150, 0.05, "Deleting Subnet " + subnetId)

        # Delete Route Tables
        rt_filter = [
            {
                'Name': 'vpc-id',
                'Values': [vpcId]
            }
        ]

        # Delete non-Main Route Tables
        listRt = []
        rts = ec2client.describe_route_tables(Filters=rt_filter)

        for rt in rts['RouteTables']:
            rtAssociations = rt['Associations']
            if rtAssociations == []:
                listRt.append(rt['RouteTableId'])
            else:
                if all(element == 'false' for element in rtAssociations):
                    listRt.append(rt['RouteTableId'])

        for rtId in listRt:
            delRt(rtId)
            aliveBar(50, 0.05, "Deleting Route Table " + rtId)

        # list all security group in VPC
        sg_filter = [
            {
                'Name': 'vpc-id',
                'Values': [str(vpcId)]
            }
        ]
        sgResponse = ec2client.describe_security_groups(Filters=sg_filter)
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
                ec2client.revoke_security_group_ingress(
                    GroupId=sgInfo['Id'], SecurityGroupRuleIds=ingressRules)
                time.sleep(5)
            if egressRules:
                ec2client.revoke_security_group_egress(
                    GroupId=sgInfo['Id'], SecurityGroupRuleIds=egressRules)
                time.sleep(5)

        # delete security groups...
        for sgInfo in listSgInfo:
            if sgInfo['GroupName'] != 'default':
                print('Deleting Security Group', sgInfo['Id'])
                delSg(sgInfo['Id'])
                time.sleep(2)

        time.sleep(45)
        ec2client.delete_vpc(VpcId=vpcId)


def listCftStack():
    """
    return a list of CFT stacks 
    """
    response = cftclient.describe_stacks()
    stacks = response['Stacks']
    listStackName = []
    for stack in stacks:
        listStackName.append(stack['StackName'])
    return listStackName


def capic(stackName):
    """
    return True if the stack stackName is Cloud APIC CFT stack
    stack's description is used to recognize Cloud APIC CFT stack
    """
    capicStack = cftclient.describe_stacks(StackName=stackName)
    x1 = capicStack['Stacks']
    capicText = 'This template creates the environment to launch a cloud APIC cluster in an AWS environment.'

    for x2 in x1:
        try:
            if x2['Description'] and capicText in x2['Description']:
                return True
        except KeyError:
            return False


def capicStackToFile(listStackName):
    """
    return Cloud APIC CFT stack name
    """
    for stackName in listStackName:
        if capic(stackName):
            return stackName


def delStack(StackName):
    """
    delete Cloud APIC CFT stack name
    """
    cftclient.delete_stack(StackName=StackName)


def listResourceGroup():
    listRg = []
    listCapicRg = []
    resources = resourcesclient.list_groups()

    try:
        listRg.append(resources['GroupIdentifiers'][0]['GroupName'])
        for rg in listRg:
            if 'CAPIC' in rg:
                listCapicRg.append(rg)
    
        return listCapicRg
    except IndexError:
        print("There is no resource group.")

def delete_group(rg):
    response = resourcesclient.delete_group(Group=rg)


def separator():
    print("======================================================================================================")


def main():
    # progressive bar
    aliveBar(100, 0.05, 'Displaying current inventory status...')
    separator()
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
    print("Security Groups:")
    listSgInfo = listSg()
    for sgInfo in listSgInfo:
        print('Security Group Name:', sgInfo['GroupName'], '|', sgInfo['Id'], sgInfo['VpcId'], '|', 'IngressRuleGroup:',
              sgInfo['IngressSecGroup'], '|', 'EgressRuleGroup:', sgInfo['EgressSecGroup'])

    # Display Internet Gateways info
    separator()
    print("Internet Gateway current information:")
    listIgwInfo = listIgw()
    for igwInfo in listIgwInfo:
        print(igwInfo['Id'], '-->', 'State',
              igwInfo['State'], '-->', igwInfo['VpcId'])

    # Display VPC info
    separator()
    listVpcInfo = listVpc()
    listVpcId = []
    for vpcInfo in listVpcInfo:
        listVpcId.append(vpcInfo['Id'])
        print(vpcInfo['Id'], '-->', 'State', vpcInfo['State'])

    # Display Transit Gateway info
    tgws = listTgw()
    print("Transit Gateways...")
    for tgw in tgws:
        print("Transit Gateway:", tgw['Id'], 'with', 'State:', tgw['State'])

    # Display Transit Gateway Peering Attachments
    separator()
    # Display Transit Gateway Peering Attachments
    print("Transit Gateway Peering Attachments:")
    nondeletedTgwPeeringAttachments = []
    listTgwState = []
    for tgw in tgws:
        listTgwState.append(tgw['State'])
        if tgw['State'] not in ['deleted', 'deleting']:
            tgwPeerings = listTgwPeering(tgw['Id'])
            if tgwPeerings:
                for tgwPeering in tgwPeerings:
                    print("TGW Attachment",
                          tgwPeering['Id'], "-->", "State", tgwPeering['State'])
                    if tgwPeering['State'] not in ['deleted', 'deleting']:
                        nondeletedTgwPeeringAttachments.append(
                            tgwPeering['Id'])

    if all(element in ['deleted', 'deleting'] for element in listTgwState):
        print("--> There is no TGW Peering Attachments")

    # Display Transit Gateway Connect Attachments
    separator()
    print("Transit Gateway Connect Attachments:")
    nondeletedTgwConnectAttachments = []
    for tgw in tgws:
        tgwConnects = listTgwConnect(tgw['Id'])
        for tgwConnect in tgwConnects:
            print("TGW:", tgw['Id'], "-->", "TGW Connect:",
                  tgwConnect['Id'], "-->", "State:", tgwConnect['State'])
            if tgwConnect['State'] not in ['deleted', 'deleting']:
                nondeletedTgwConnectAttachments.append(tgwConnect['Id'])

    # Display Transit Gateway Connect Peers
    separator()
    print("Transit Gateway Connect Peers:")
    nondeletedTgwConnectPeers = []
    listTgwConnectPeerState = []
    for tgw in tgws:
        tgwConnects = listTgwConnect(tgw['Id'])
        for tgwConnect in tgwConnects:
            tgwConnectPeers = listTgwConnectPeer(tgwConnect['Id'])
            for tgwConnectPeer in tgwConnectPeers:
                print("TGW Connect", tgwConnect['Id'], "-->", "Peer:",
                      tgwConnectPeer['Id'], "State", tgwConnectPeer['State'])
                listTgwConnectPeerState.append(tgwConnectPeer['State'])
                if tgwConnectPeer['State'] not in ['deleted', 'deleting']:
                    nondeletedTgwConnectPeers.append(tgwConnectPeer['Id'])

    # Display Transit Gateway Connect Peer in avaialble state
    separator()
    print("TGW Connect Peers in avaiable state:")

    if all(element in ['deleting', 'deleted'] for element in listTgwConnectPeerState):
        print("--> There is no TGW Peers in avaiable state")

    for nondeletedTgwConnectPeer in nondeletedTgwConnectPeers:
        print(nondeletedTgwConnectPeer)
    # Decomissioning process
    separator()
    print('Start decomissioning process.')
    print('Delete all TGW related objects.')
    print('Terminate Instances and then terminate VPC.')
    print('This process is destructive!!!')

    # progressive bar
    aliveBar(100, 0.05, 'Start decomission TGW, VPC, Instances...')

    if nondeletedTgwPeeringAttachments != []:
        print("Deleting TGW Peering...")
        for nondeletedTgwPeeringAttachment in nondeletedTgwPeeringAttachments:
            delTgwPeering(nondeletedTgwPeeringAttachment)
            aliveBar(5000 + randrange(100, 200), 0.05,
                     "Deleting TGW Peering " + nondeletedTgwPeeringAttachment)
    else:
        print('There is no TGW peering exists')

    if nondeletedTgwConnectAttachments != []:
        print("Deleting TGW Connect Attachments....")
        for nondeletedTgwConnectAttachment in nondeletedTgwConnectAttachments:
            delTgwConnect(nondeletedTgwConnectAttachment)
    else:
        print("All TGW Connect Attachments are gone.")

    separator()
    print("Delete TGW VPC Attachments...")
    for tgw in tgws:
        tgwVpcAttachments = listTgwVpcAttachment(tgw['Id'])
        for tgwVpcAttachment in tgwVpcAttachments:
            print('TGW VPC Attachment->', tgwVpcAttachment['Id'], '-->',
                  'State:', tgwVpcAttachment['State'])

    eligibleTgwVpcAttachment = []
    for tgw in tgws:
        tgwVpcAttachments = listTgwVpcAttachment(tgw['Id'])
        for tgwVpcAttachment in tgwVpcAttachments:
            if tgwVpcAttachment['State'] not in ['deleted', 'deleting']:
                eligibleTgwVpcAttachment.append(tgwVpcAttachment['Id'])
                delTgwVpcAttachment(tgwVpcAttachment['Id'])

    # progressive bar
    for tgwVpcAttachment in eligibleTgwVpcAttachment:
        aliveBar(2000 + randrange(100, 200), 0.05,
                 "Deleting VPC Attachment " + tgwVpcAttachment)

    separator()
    print("Delete TGW...")
    eligibleTgw = []
    for tgw in tgws:
        if tgw['State'] not in ['deleted', 'deleting']:
            #print('Deleting TGW,', tgw['Id'])
            eligibleTgw.append(tgw['Id'])
            delTgw(tgw['Id'])

    # progressive bar
    for tgw in eligibleTgw:
        aliveBar(2500 + randrange(100, 200), 0.05, "Deleting TGW " + tgw)

    print("All Transit Gateways are deleted, starting decomissioning instances and VPC.")

    # progressive bar
    aliveBar(150, 0.05, 'Taking some rest..')

    # terminate instances
    if terminatedFlag:
        print('--> Start terminating instances...')
        for i in range(len(listInstanceId)):
            singleInstance = []
            singleInstance.append(listInstanceId[i])
            #print('Terminating instance', singleInstance)
            terminateInstance(singleInstance)

     # progressive bar
    if len(listInstanceId) == 1:
        for ins in listInstanceId:
            aliveBar(2500 + randrange(100, 200), 0.05, "Terminating " + ins)
    elif len(listInstanceId) == 2:
        for ins in listInstanceId:
            aliveBar(1500 + randrange(100, 200), 0.05, "Terminating " + ins)
    else:
        for ins in listInstanceId:
            aliveBar(1000 + randrange(100, 200), 0.05, "Terminating " + ins)

    eip = listEip()
    if eip != []:
        separator()
        print('Disassocating and releasing instances EIP...')
        for ip in eip:
            if ip['AssociationId'] != None:
                disAssociateEip(ip['AssociationId'])
                aliveBar(50 + randrange(10, 20), 0.05,
                         "Disassociating " + ip['PublicIp'])

            releaseEip(ip['AllocationId'])
            aliveBar(50 + randrange(10, 20), 0.05,
                     "Releasing " + ip['PublicIp'])

    cApicEip = listcApicEip()
    if cApicEip != []:
        separator()
        print('Disassocating and releasing cAPIC EIP')
        for ip in cApicEip:
            if ip['AssociationId'] != None:
                disAssociateEip(ip['AssociationId'])
                time.sleep(5)
                aliveBar(50 + randrange(10, 20), 0.05,
                         "Disassociating " + ip['PublicIp'])
            releaseEip(ip['AllocationId'])
            aliveBar(70 + randrange(10, 20), 0.05,
                     "Releasing EIP " + ip['PublicIp'])

    # Deleting All ENIs
    eni = listcApicInfraEni()
    if eni:
        separator()
        print('Delete cApic Infra ENI...')
        for e in eni:
            delEni(e)
            aliveBar(70 + randrange(10, 20), 0.05, "Deleting Infra ENI " + e)

    oobeni = listcApicOobEni()
    if oobeni:
        separator()
        print('Delete cApic OOB ENI...')
        for e in oobeni:
            delEni(e)
            aliveBar(70 + randrange(10, 20), 0.05,
                     "Deleting Out-of-band ENI " + e)
    # Deleting VPC
    print('--> Start deleting VPC...')

    if listVpcId == []:
        print('There is no active VPC in the account.')
    else:
        for vpcId in listVpcId:
            delVpc(vpcId)

        # progressive bar
        for vpc in listVpcId:
            aliveBar(300 + randrange(50, 100), 0.05, "Deleting " + vpc)

        print('All VPCs are gone !!! Goodbye !!!')

    listStackName = listCftStack()
    if listStackName != []:
        cftcapic = capicStackToFile(listStackName)
        if cftcapic:
            print('Delete Cloud formation template', cftcapic)
            delStack(cftcapic)
            # progressive bar
            aliveBar(1000, 0.05, 'Delete cft template...')
        else:
            print('There is no Cloud APIC CFT.')

    print("Checking resources group")
    listCapicRg = listResourceGroup()

    if listCapicRg == None:
        print('No resource exist.')
    else:
        for rg in listCapicRg:
            print(rg)
            delete_group(rg)
        
    print('Done, all resources are completely gone!!!')


if __name__ == "__main__":
    main()
