terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.4.0"
    }
  }
}

provider "aws" {
  access_key = var.access_key
  secret_key = var.secret_key
  region = var.region
}

variable "aws-capic" {
  default = "/Users/huyeduon/DATA/TME/labops/aws/provisioning/capic/capic_single_cft.json"
}

resource "aws_cloudformation_stack" "capic" {
  name = "capic-stack"
  capabilities = ["CAPABILITY_NAMED_IAM"]
  parameters = {
        "pInfraVPCPool": var.pInfraVPCPool, 
        "pFabricName": var.pFabricName,
        "pAvailabilityZone": var.pAvailabilityZone,
        "pInstanceType": var.pInstanceType,
        "pExtNw": var.pExtNw,
        "pPassword": var.pPassword, 
        "pConfirmPassword": var.pConfirmPassword, 
        "pKeyName": var.pKeyName,
        "pAssignOOBIntfEIP": "true"
  }

  template_body = "${file(var.aws-capic)}"
}

# output cAPIC OOB IP address
data "aws_instance" "capic" {
  instance_tags = {
    Name = "Capic-1"
  }
  depends_on = [
    aws_cloudformation_stack.capic
  ]
}

output "capicOobIp" {
  value = data.aws_instance.capic.public_ip
}