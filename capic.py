#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The script will deploy Cisco Cloud APIC in us-east-1 region
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
