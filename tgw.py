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
ec2client = session.client('ec2', config=htduong)

custom_filter = [
    {
        'Name': 'tag:owner',
        'Values': ['huyen']
    }

]

def listTgw():
    # return a list of TGW has tag key=owner, value=huyen
    listTgwInfo = []
    tgw = ec2client.describe_transit_gateways(Filters=custom_filter)
    for x2 in tgw['TransitGateways']:
        tgwInfo = {}
        tgwInfo['Id'] = x2['TransitGatewayId']
        tgwInfo['State'] = x2['State']
        listTgwInfo.append(tgwInfo)

    return listTgwInfo


def listTgwVpcAttachment(tgwId):
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

def listTgwConnect(tgw):
    # return a list of TGW Connect Attachment
    newfilter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgw)]
        }
    ]
    listTgwConnectInfo = []
    tgwConnectId = ec2client.describe_transit_gateway_connects(Filters=newfilter)
    for tgwConnect in tgwConnectId['TransitGatewayConnects']:
        tgwConnectInfo = {}
        tgwConnectInfo['Id'] = tgwConnect['TransitGatewayAttachmentId']
        tgwConnectInfo['State'] = tgwConnect['State']
        listTgwConnectInfo.append(tgwConnectInfo)

    return listTgwConnectInfo

def listTgwConnectPeer(tgwConnectAttachId):
    # return a list of tgw connect peer
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


def listTgwPeering(tgw):
    newfilter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgw)]
        }
    ]
    listTgwPeeringInfo = []
    response = ec2client.describe_transit_gateway_peering_attachments(Filters=newfilter)
    tgwPeeringAttachments = response['TransitGatewayPeeringAttachments']
    for twgPeeringAttachment in tgwPeeringAttachments:
        tgwPeeringInfo = {}
        tgwPeeringInfo['Id'] = tgwPeeringAttachments['TransitGatewayAttachmentId']
        tgwPeeringInfo['State'] = tgwPeeringAttachments['State']
        listTgwPeeringInfo.append(tgwPeeringInfo)

    return listTgwPeeringInfo

# delete tgw connect peer
def delTgwConnectPeer(connectPeerId):
    ec2client.delete_transit_gateway_connect_peer(
        TransitGatewayConnectPeerId=connectPeerId)

# delete tgw connnect attachment
def delTgwConnect(connectAttachmentId):
    # check if it is possible to delete tgwConnect attachment
    # only delete tgwConnect attachment if all connectPeers are in deleted state 
    eligibleDeletion = False

    listTgwConnectPeerInfo = listTgwConnectPeer(connectAttachmentId)
    # delete all connect peers who are not in deleted or deleting state.
    for tgwConnectPeerInfo in listTgwConnectPeerInfo:
        if tgwConnectPeerInfo['State'] not in ['deleted', 'deleting']:
            print("Deleting TGW Connect Peer",
                  tgwConnectPeerInfo['Id'], "in", connectAttachmentId)
            delTgwConnectPeer(tgwConnectPeerInfo['Id'])

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

    print("Deleting TGW Connect Attachment ",connectAttachmentId)

    if eligibleDeletion:
        ec2client.delete_transit_gateway_connect(TransitGatewayAttachmentId=connectAttachmentId)  

def delTgwVpcAttachment(tgwVpcAttachmentId):
    # find all tgwConnectAttachment who use that vpc as transport attachmentInfoList
    # if tgwConnectAttachment state is deleted then we can delete VPC attachment

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
                print("All Connect Attachments are in deleted state, start deleting VPC Attachment...")

    print("Deleting TGW VPC Attachment", tgwVpcAttachmentId)

    if eligibleDeletion:
        ec2client.delete_transit_gateway_vpc_attachment(TransitGatewayAttachmentId=tgwVpcAttachmentId)
 

def delTgw(tgwId):
    eligibleDeletion = False
    newfilter = [
        {
            'Name': 'transit-gateway-id',
            'Values': [str(tgwId)]
        }
    ]
 
    while not eligibleDeletion:
        time.sleep(45)
        response = ec2client.describe_transit_gateway_attachments(
            Filters=newfilter)
       
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


def separator():
    print("================================================")

def minusLine():
    print("------------------------------------------------")

def main():
    tgws = listTgw()
    print("Transit Gateways...")
    for tgw in tgws:
        print("Transit Gateway:", tgw['Id'],'with', 'State:', tgw['State'])

    separator()
    print("Transit Gateway Peering Attachments:")
    listTgwState = []
    for tgw in tgws:
        listTgwState.append(tgw['State'])
        if tgw['State'] not in ['deleted', 'deleting']:
            tgwPeerings = listTgwPeering(tgw['Id'])
            if tgwPeerings:
                for tgwPeering in tgwPeerings:
                    print("TGW Attachment", tgwPeering['Id'],"-->","State", tgwPeering['State'])
    
    if all(element in ['deleted','deleting'] for element in listTgwState):
        print("--> There is no TGW Peering Attachments")

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

    separator()
    print("TGW Connect Peers:")
    nondeletedTgwConnectPeers = []
    listTgwConnectPeerState = []
    for tgw in tgws:
        tgwConnects = listTgwConnect(tgw['Id'])
        for tgwConnect in tgwConnects:
            tgwConnectPeers = listTgwConnectPeer(tgwConnect['Id'])
            for tgwConnectPeer in tgwConnectPeers:
                print("TGW Connect", tgwConnect['Id'], "-->", "Peer:", tgwConnectPeer['Id'],"State", tgwConnectPeer['State'])
                listTgwConnectPeerState.append(tgwConnectPeer['State'])
                if tgwConnectPeer['State'] not in ['deleted', 'deleting']:
                    nondeletedTgwConnectPeers.append(tgwConnectPeer['Id'])

    separator()

    print("TGW Connect Peers in avaiable state:")
    
    if all(element in ['deleting','deleted'] for element in listTgwConnectPeerState):
        print("--> There is no TGW Peers in avaiable state")

    for nondeletedTgwConnectPeer in nondeletedTgwConnectPeers:
        print(nondeletedTgwConnectPeer)
    
    separator()
    
    print("Start decommissioning...")
    
    if nondeletedTgwConnectAttachments != []:
        print("Deleting TGW Connect Attachments....")
        for nondeletedTgwConnectAttachment in nondeletedTgwConnectAttachments:
            delTgwConnect(nondeletedTgwConnectAttachment)
    else:
        print("All TGW Connect Attachments are gone.")
    
    print("TGW VPC Attachments:")
    for tgw in tgws:
        tgwVpcAttachments = listTgwVpcAttachment(tgw['Id'])
        for tgwVpcAttachment in tgwVpcAttachments:
            print(tgwVpcAttachment['Id'],'-->', 'State:', tgwVpcAttachment['State'])
    
    print("Deleting TGW VPC Attachments............")

    for tgw in tgws:
        tgwVpcAttachments = listTgwVpcAttachment(tgw['Id'])
        for tgwVpcAttachment in tgwVpcAttachments:
            if tgwVpcAttachment['State'] not in ['deleted', 'deleting']:
                delTgwVpcAttachment(tgwVpcAttachment['Id'])

    separator()
    print("Deleting TGW........................")
    for tgw in tgws:
        if tgw['State'] not in ['deleted', 'deleting']:
            print('Deleting TGW,', tgw['Id'])
            delTgw(tgw['Id'])
           
    print("All Transit Gateways are deleted, please wait a few mins before proceed.")

if __name__ == "__main__":
    main()
