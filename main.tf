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

# create VPC

resource "aws_vpc" "vpc1" {
  cidr_block = "10.1.0.0/16"
 tags = {
    Name = "vpc1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_vpc" "vpc2" {
  cidr_block = "10.2.0.0/16"
  tags = {
    Name = "vpc2"
    AciOwnerTag = "huyen"
  }
}

# create Subnet

resource "aws_subnet" "net1vpc1" {
  vpc_id     = aws_vpc.vpc1.id
  cidr_block = "10.1.1.0/24"

  tags = {
    Name = "net1vpc1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net2vpc1" {
  vpc_id     = aws_vpc.vpc1.id
  cidr_block = "10.1.2.0/24"

  tags = {
    Name = "net2vpc1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net3vpc1" {
  vpc_id     = aws_vpc.vpc1.id
  cidr_block = "10.1.3.0/24"

  tags = {
    Name = "net3vpc1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net4vpc1" {
  vpc_id     = aws_vpc.vpc1.id
  cidr_block = "10.1.4.0/24"

  tags = {
    Name = "net4vpc1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net1vpc2" {
  vpc_id     = aws_vpc.vpc2.id
  cidr_block = "10.2.1.0/24"

  tags = {
    Name = "net1vpc2"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net2vpc2" {
  vpc_id     = aws_vpc.vpc2.id
  cidr_block = "10.2.2.0/24"

  tags = {
    Name = "net2vpc2"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net3vpc2" {
  vpc_id     = aws_vpc.vpc2.id
  cidr_block = "10.2.3.0/24"

  tags = {
    Name = "net3vpc2"
    AciOwnerTag = "huyen"
  }
}

resource "aws_subnet" "net4vpc2" {
  vpc_id     = aws_vpc.vpc2.id
  cidr_block = "10.2.4.0/24"

  tags = {
    Name = "net4vpc2"
    AciOwnerTag = "huyen"
  }
}

# create IGW

resource "aws_internet_gateway" "igw1" {
  vpc_id = aws_vpc.vpc1.id
  tags = {
    Name = "igw1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_internet_gateway" "igw2" {
  vpc_id = aws_vpc.vpc2.id
  tags = {
    Name = "igw2"
    AciOwnerTag = "huyen"
  }
}


# Create route table

resource "aws_route_table" "net1vpc1rt" {
  vpc_id = aws_vpc.vpc1.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw1.id
  }

  tags = {
    Name = "net1vpc1rt"
    AciOwnerTag = "huyen"
  }
}

resource "aws_route_table" "net1vpc2rt" {
  vpc_id = aws_vpc.vpc2.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw2.id
  }

  tags = {
    Name = "net1vpc2rt"
    AciOwnerTag = "huyen"
  }
}

# Associate route table with subnet
resource "aws_route_table_association" "vpc1net1" {
  subnet_id      = aws_subnet.net1vpc1.id
  route_table_id = aws_route_table.net1vpc1rt.id
}


resource "aws_route_table_association" "vpc2net1" {
  subnet_id      = aws_subnet.net1vpc2.id
  route_table_id = aws_route_table.net1vpc2rt.id
}

# Create TGW, Attachment, Connect Peers...

resource "aws_ec2_transit_gateway" "tgw1" {
  description = "tgw1"
  default_route_table_association = "enable"
  transit_gateway_cidr_blocks=["172.16.11.0/24"]
  tags = {
    Name = "tgw1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "vpc1" {
  subnet_ids         = [aws_subnet.net1vpc1.id]
  transit_gateway_id = aws_ec2_transit_gateway.tgw1.id
  vpc_id             = aws_vpc.vpc1.id
  tags = {
    Name = "vpc1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "vpc2" {
  subnet_ids         = [aws_subnet.net1vpc2.id]
  transit_gateway_id = aws_ec2_transit_gateway.tgw1.id
  vpc_id             = aws_vpc.vpc2.id
  tags = {
    Name = "vpc2"
    AciOwnerTag = "huyen"
  }
}

# Create transit gateway connect

resource "aws_ec2_transit_gateway_connect" "connect1" {
  transport_attachment_id = aws_ec2_transit_gateway_vpc_attachment.vpc1.id
  transit_gateway_id      = aws_ec2_transit_gateway.tgw1.id
  tags = {
    Name = "connect1"
    AciOwnerTag = "huyen"
  }
}


resource "aws_ec2_transit_gateway_connect" "connect2" {
  transport_attachment_id = aws_ec2_transit_gateway_vpc_attachment.vpc2.id
  transit_gateway_id      = aws_ec2_transit_gateway.tgw1.id
   tags = {
    Name = "connect2"
    AciOwnerTag = "huyen"
  }
}

# Create transit gateway connect peer
resource "aws_ec2_transit_gateway_connect_peer" "peer1connect1" {
  peer_address                  = "10.1.1.1"
  inside_cidr_blocks            = ["169.254.111.0/29"]
  transit_gateway_attachment_id = aws_ec2_transit_gateway_connect.connect1.id
  tags = {
    Name = "peer1connect1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_ec2_transit_gateway_connect_peer" "peer2connect1" {
  peer_address                  = "10.1.2.1"
  inside_cidr_blocks            = ["169.254.112.0/29"]
  transit_gateway_attachment_id = aws_ec2_transit_gateway_connect.connect1.id
  tags = {
    Name = "peer2connect1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_ec2_transit_gateway_connect_peer" "peer1connect2" {
  peer_address                  = "10.1.21.1"
  inside_cidr_blocks            = ["169.254.121.0/29"]
  transit_gateway_attachment_id = aws_ec2_transit_gateway_connect.connect2.id
  tags = {
    Name = "peer1connect2"
    AciOwnerTag = "huyen"
  }
}

resource "aws_ec2_transit_gateway_connect_peer" "peer2connect2" {
  peer_address                  = "10.1.22.1"
  inside_cidr_blocks            = ["169.254.122.0/29"]
  transit_gateway_attachment_id = aws_ec2_transit_gateway_connect.connect2.id
  tags = {
    Name = "peer2connect2"
    AciOwnerTag = "huyen"
  }
}

# create security group
resource "aws_security_group" "vpc1sg" {
  name = "vpc1sg"
  description = "vpc1 security group"
  vpc_id = aws_vpc.vpc1.id

  tags = {
    Name = "vpc1sg"
    AciOwnerTag = "huyen"
  }
}

resource "aws_security_group" "vpc2sg" {
  name = "vpc2sg"
  description = "vpc2 security group"
  vpc_id = aws_vpc.vpc2.id
  
  tags = {
    Name = "vpc2sg"
    AciOwnerTag = "huyen"
  }
}

resource "aws_security_group" "mix12sg" {
  name = "mix12sg"
  description = "mix12 security group"
  vpc_id = aws_vpc.vpc1.id

  tags = {
    Name = "mix12sg"
    AciOwnerTag = "huyen"
  }
}

resource "aws_security_group" "mix21sg" {
  name = "mix21sg"
  description = "mix21 security group"
  vpc_id = aws_vpc.vpc2.id

  tags = {
    Name = "mix21sg"
    AciOwnerTag = "huyen"
  }
}


# Create Security Group Rules

resource "aws_security_group_rule" "vpc1allowicmp" {
  type = "ingress"
  from_port = -1
  protocol = "icmp"
  to_port  = -1
  security_group_id = aws_security_group.vpc1sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "vpc1allowssh" {
  type = "ingress"
  from_port = 22
  protocol = "tcp"
  to_port = 22
  security_group_id = aws_security_group.vpc1sg.id
  source_security_group_id = aws_security_group.vpc1sg.id
}

resource "aws_security_group_rule" "vpc1allowhttp" {
  type = "ingress"
  from_port = 80
  protocol = "tcp"
  to_port = 80
  security_group_id = aws_security_group.vpc1sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "vpc1all" {
  type = "egress"
  from_port = 0
  protocol = "-1"
  to_port = 0
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.vpc1sg.id
}


resource "aws_security_group_rule" "vpc2allowicmp" {
  type = "ingress"
  from_port = -1
  protocol = "icmp"
  to_port = -1
  security_group_id = aws_security_group.vpc2sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "vpc2allowssh" {
  type = "ingress"
  from_port = 22
  protocol = "tcp"
  to_port = 22
  security_group_id = aws_security_group.vpc2sg.id
  source_security_group_id = aws_security_group.vpc2sg.id
}

resource "aws_security_group_rule" "vpc2allowhttp" {
  type = "ingress"
  from_port = 80
  protocol = "tcp"
  to_port = 80
  security_group_id = aws_security_group.vpc2sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "vpc2all" {
  type = "egress"
  from_port = 0
  protocol = "-1"
  to_port = 0
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.vpc2sg.id
}

resource "aws_security_group_rule" "mix12allowssh" {
  type = "ingress"
  from_port = 22
  protocol = "tcp"
  to_port = 22
  security_group_id = aws_security_group.mix12sg.id
  source_security_group_id = aws_security_group.vpc1sg.id
}

resource "aws_security_group_rule" "mix12allowhttp" {
  type = "ingress"
  from_port = 80
  protocol = "tcp"
  to_port = 80
  security_group_id = aws_security_group.mix12sg.id
  source_security_group_id = aws_security_group.vpc1sg.id
}

resource "aws_security_group_rule" "mix12all" {
  type = "egress"
  from_port = 0
  protocol = "-1"
  to_port = 0
  security_group_id = aws_security_group.mix12sg.id
  source_security_group_id = aws_security_group.vpc1sg.id
}


resource "aws_security_group_rule" "mix21allowssh" {
  type = "ingress"
  from_port = 22
  protocol = "tcp"
  to_port = 22
  security_group_id = aws_security_group.mix21sg.id
  source_security_group_id = aws_security_group.vpc2sg.id
}

resource "aws_security_group_rule" "mix21allowhttp" {
  type = "ingress"
  from_port = 80
  protocol = "tcp"
  to_port = 80
  security_group_id = aws_security_group.mix21sg.id
  source_security_group_id = aws_security_group.vpc2sg.id
}

resource "aws_security_group_rule" "mix21all" {
  type = "egress"
  from_port = 0
  protocol = "-1"
  to_port = 0
  security_group_id = aws_security_group.mix21sg.id
  source_security_group_id = aws_security_group.vpc2sg.id
}


# create instances

resource "aws_instance" "web1" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.net1vpc1.id
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.vpc1sg.id
  ]

  key_name = "htduong-us-east-1"

  tags = {
    Name = "web1"
    AciOwnerTag = "huyen"
  }
}

resource "aws_instance" "web2" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.net1vpc2.id
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.vpc2sg.id
  ]

  key_name = "htduong-us-east-1"

  tags = {
    Name = "web2"
    AciOwnerTag = "huyen"
  }
}

# output instances private and public IP addresses

output "web1-private-ip" {
  value = aws_instance.web1.private_ip
}

output "web1-public-ip" {
  value = aws_instance.web1.public_ip
}

output "web2-private-ip" {
  value = aws_instance.web2.private_ip
}

output "web2-public-ip" {
  value = aws_instance.web2.public_ip
}
