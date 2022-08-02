#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Requirements: python3, boto3, aws cli
# This script will deploy cAPIC

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

