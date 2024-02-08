#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3
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

htduong08 = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

session = boto3.session.Session(profile_name='htduong08')
ec2client = session.client('ec2', config=htduong08)
cftclient = session.client('cloudformation', config=htduong08)

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
        eipInfo['AssociationId'] = eip['AssociationId']
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
        eipInfo['AssociationId'] = eip['AssociationId']
        listcApicEipInfo.append(eipInfo)

    return listcApicEipInfo


def disAssociateEip(associationId):
    """
    dis-associate EIP from instances
    """
    ec2client.disassociate_address(AssociationId=associationId)


def releaseEip(allocId):
    """
    release EIP
    """
    ec2client.release_address(AllocationId=allocId)


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
    capic = cftclient.describe_stacks(StackName=stackName)
    x1 = capic['Stacks']
    capicText = 'This template creates the environment to launch a cloud APIC cluster in an AWS environment.'

    for x2 in x1:
        try:
            if x2['Description'] and capicText in x2['Description']:
                return True
        except KeyError:
            exit()

def capicStackToFile(listStackName):
    """
    return Cloud APIC CFT stack name
    """
    for stackName in listStackName:
        if capic(stackName):
            return stackName


def listResourceGroup():
    resources = resourcesclient.list_groups(
        Filters=[ 
            { 
                'Name': 'CAPIC?*'
            }
    ])
    return resources['GroupIdentifiers'][0]['GroupName']

def separator():
    print("======================================================================================================")

def minusLine():
    print("-------------------------------------------------------------------------------------------------------")


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
   
    '''
    print("Security Groups:")
    listSgInfo = listSg()
    for sgInfo in listSgInfo:
        print('Security Group Name:', sgInfo['GroupName'], '|', sgInfo['Id'], sgInfo['VpcId'], '|', 'IngressRuleGroup:',
              sgInfo['IngressSecGroup'], '|', 'EgressRuleGroup:', sgInfo['EgressSecGroup'])
    '''
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
    separator()

    listStackName = listCftStack()
    capicStack = capicStackToFile(listStackName)
    if capicStack:
        print('Cloud APIC Stack name: ', capicStack)
    else:
        print('There is no Cloud APIC Stack.')


    print("Checking resources group")
    rg = listResourceGroup()
    print(rg)

if __name__ == "__main__":
    main()
