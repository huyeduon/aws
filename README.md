# Requirements to run python script:
Boto3
alive_progress
..............
For detai, pls look at file requirements.txt

# Terraform to build test infra
You need to create terraform.tfvars with content similar:

access_key = ""
secret_key = ""
region     = "us-east-1"

Then run terraform against main.tf file.
The main.tf script will create: VPCs, Instances, TGW, TGW Attachment, TGW Connect, Security Groups, Internet Gateway.
Remember to set the tag to what you want.

The tag using in main.tf file:

tags = {
    Name = "vpc1",
    owner = "huyen"
}

The custom filter in infraDecom.py file:

custom_filter = [
    {
        'Name': 'tag:owner',
        'Values': ['huyen']
    }

]

owner in tag in main.tf must match Values in custom_filter.

This is what you needed to test decomission script.

# Run the script to decommssion:

python3 infraDecom.py

