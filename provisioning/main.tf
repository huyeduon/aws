terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.22.0"
    }
  }
}

provider "aws" {
  access_key = var.access_key
  secret_key = var.secret_key
  region = var.region
}

# create VPC

resource "aws_vpc" "brown1" {
  cidr_block = "10.198.1.0/24"
 tags = {
    Name = "brown1"
  }
}

resource "aws_vpc" "brown2" {
  cidr_block = "10.198.2.0/24"
  tags = {
    Name = "brown2"
  }
}

resource "aws_vpc" "brown3" {
  cidr_block = "10.198.3.0/24"
  tags = {
    Name = "brown3"
  }
}


# create Subnet
resource "aws_subnet" "net1brown1" {
  vpc_id     = aws_vpc.brown1.id
  cidr_block = "10.198.1.0/28"

  tags = {
    Name = "net1brown1"
  }
}

resource "aws_subnet" "net2brown1" {
  vpc_id     = aws_vpc.brown1.id
  cidr_block = "10.198.1.16/28"

  tags = {
    Name = "net2brown1"
  }
}

resource "aws_subnet" "net3brown1" {
  vpc_id     = aws_vpc.brown1.id
  cidr_block = "10.198.1.32/28"

  tags = {
    Name = "net3brown1"
  }
}


resource "aws_subnet" "net4brown1" {
  vpc_id     = aws_vpc.brown1.id
  cidr_block = "10.198.1.48/28"

  tags = {
    Name = "net4brown1"
  }
}

resource "aws_subnet" "net1brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.0/28"

  tags = {
    Name = "net1brown2"
  }
}

resource "aws_subnet" "net2brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.16/28"

  tags = {
    Name = "net2brown2"
  }
}

resource "aws_subnet" "net3brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.32/28"

  tags = {
    Name = "net3brown2"
  }
}


resource "aws_subnet" "net4brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.48/28"

  tags = {
    Name = "net4brown2"
  }
}

resource "aws_subnet" "net5brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.64/28"

  tags = {
    Name = "net5brown2"
  }
}

resource "aws_subnet" "net6brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.80/28"

  tags = {
    Name = "net6brown2"
  }
}

resource "aws_subnet" "net7brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.96/28"

  tags = {
    Name = "net7brown2"
  }
}


resource "aws_subnet" "net8brown2" {
  vpc_id     = aws_vpc.brown2.id
  cidr_block = "10.198.2.112/28"

  tags = {
    Name = "net8brown2"
  }
}

resource "aws_subnet" "net1brown3" {
  vpc_id     = aws_vpc.brown3.id
  cidr_block = "10.198.3.0/28"

  tags = {
    Name = "net1brown3"
  }
}



resource "aws_subnet" "net2brown3" {
  vpc_id     = aws_vpc.brown3.id
  cidr_block = "10.198.3.16/28"

  tags = {
    Name = "net2brown3"
  }
}

resource "aws_subnet" "net3brown3" {
  vpc_id     = aws_vpc.brown3.id
  cidr_block = "10.198.3.32/28"

  tags = {
    Name = "net3brown3"
  }
}


resource "aws_subnet" "net4brown3" {
  vpc_id     = aws_vpc.brown3.id
  cidr_block = "10.198.3.48/28"

  tags = {
    Name = "net4brown3"
  }
}


# create IGW
resource "aws_internet_gateway" "brown1" {
  vpc_id = aws_vpc.brown1.id
  tags = {
    Name = "brown1"
  }
}

resource "aws_internet_gateway" "brown2" {
  vpc_id = aws_vpc.brown2.id
  tags = {
    Name = "brown2"
  }
}

resource "aws_internet_gateway" "brown3" {
  vpc_id = aws_vpc.brown3.id
  tags = {
    Name = "brown3"
  }
}

# Create TGW, Attachment
resource "aws_ec2_transit_gateway" "browntgw" {
  description = "browntgw"
  default_route_table_association = "enable"
  tags = {
    Name = "browntgw"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "brown1" {
  subnet_ids         = [aws_subnet.net1brown1.id]
  transit_gateway_id = aws_ec2_transit_gateway.browntgw.id
  vpc_id             = aws_vpc.brown1.id
  tags = {
    Name = "brown1"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "brown2" {
  subnet_ids         = [aws_subnet.net1brown2.id]
  transit_gateway_id = aws_ec2_transit_gateway.browntgw.id
  vpc_id             = aws_vpc.brown2.id
  tags = {
    Name = "brown2"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "brown3" {
  subnet_ids         = [aws_subnet.net1brown3.id]
  transit_gateway_id = aws_ec2_transit_gateway.browntgw.id
  vpc_id             = aws_vpc.brown3.id
  tags = {
    Name = "brown3"
  }
}

# Create route table
resource "aws_route_table" "brown1" {
  vpc_id = aws_vpc.brown1.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.brown1.id
  }

  route {
    cidr_block = "10.198.2.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

   route {
    cidr_block = "10.198.3.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

  tags = {
    Name = "brown1"
  }
  depends_on = [
    aws_ec2_transit_gateway.browntgw
  ]
}

resource "aws_route_table" "brown2" {
  vpc_id = aws_vpc.brown2.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.brown2.id
  }

  route {
    cidr_block = "10.198.1.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

   route {
    cidr_block = "10.198.3.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

  tags = {
    Name = "brown2"
  }

  depends_on = [
    aws_ec2_transit_gateway.browntgw
  ]
}


resource "aws_route_table" "brown2-1" {
  vpc_id = aws_vpc.brown2.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.brown2.id
  }

  route {
    cidr_block = "10.198.1.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

   route {
    cidr_block = "10.198.3.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

  tags = {
    Name = "brown2-1"
  }

  depends_on = [
    aws_ec2_transit_gateway.browntgw
  ]
}

resource "aws_route_table" "brown2-2" {
  vpc_id = aws_vpc.brown2.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.brown2.id
  }

  route {
    cidr_block = "10.198.1.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

   route {
    cidr_block = "10.198.3.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

  tags = {
    Name = "brown2-2"
  }

  depends_on = [
    aws_ec2_transit_gateway.browntgw
  ]
}

resource "aws_route_table" "brown3" {
  vpc_id = aws_vpc.brown3.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.brown3.id
  }

  route {
    cidr_block = "10.198.1.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

   route {
    cidr_block = "10.198.2.0/24"
    gateway_id = aws_ec2_transit_gateway.browntgw.id
  }

  tags = {
    Name = "brown3"
  }

  depends_on = [
    aws_ec2_transit_gateway.browntgw
  ]

}

# Associate route table with subnet
resource "aws_route_table_association" "net1brown1" {
  subnet_id      = aws_subnet.net1brown1.id
  route_table_id = aws_route_table.brown1.id
}

resource "aws_route_table_association" "net2brown1" {
  subnet_id      = aws_subnet.net2brown1.id
  route_table_id = aws_route_table.brown1.id
}

resource "aws_route_table_association" "net3brown1" {
  subnet_id      = aws_subnet.net3brown1.id
  route_table_id = aws_route_table.brown1.id
}

resource "aws_route_table_association" "net4brown1" {
  subnet_id      = aws_subnet.net4brown1.id
  route_table_id = aws_route_table.brown1.id
}

# brown2 vpc
resource "aws_route_table_association" "net1brown2" {
  subnet_id      = aws_subnet.net1brown2.id
  route_table_id = aws_route_table.brown2.id
}

resource "aws_route_table_association" "net2brown2" {
  subnet_id      = aws_subnet.net2brown2.id
  route_table_id = aws_route_table.brown2.id
}

resource "aws_route_table_association" "net3brown2" {
  subnet_id      = aws_subnet.net3brown2.id
  route_table_id = aws_route_table.brown2.id
}

resource "aws_route_table_association" "net4brown2" {
  subnet_id      = aws_subnet.net4brown2.id
  route_table_id = aws_route_table.brown2.id


  
}

resource "aws_route_table_association" "net5brown2" {
  subnet_id      = aws_subnet.net5brown2.id
  route_table_id = aws_route_table.brown2-1.id
}

resource "aws_route_table_association" "net6brown2" {
  subnet_id      = aws_subnet.net6brown2.id
  route_table_id = aws_route_table.brown2-1.id
}

resource "aws_route_table_association" "net7brown2" {
  subnet_id      = aws_subnet.net7brown2.id
  route_table_id = aws_route_table.brown2-2.id
}

resource "aws_route_table_association" "net8brown2" {
  subnet_id      = aws_subnet.net8brown2.id
  route_table_id = aws_route_table.brown2-2.id
}

# brown3 vpc
resource "aws_route_table_association" "net1brown3" {
  subnet_id      = aws_subnet.net1brown3.id
  route_table_id = aws_route_table.brown3.id
}

resource "aws_route_table_association" "net2brown3" {
  subnet_id      = aws_subnet.net2brown3.id
  route_table_id = aws_route_table.brown3.id
}

resource "aws_route_table_association" "net3brown3" {
  subnet_id      = aws_subnet.net3brown3.id
  route_table_id = aws_route_table.brown3.id
}

resource "aws_route_table_association" "net4brown3" {
  subnet_id      = aws_subnet.net4brown3.id
  route_table_id = aws_route_table.brown3.id
}


# create security group
resource "aws_security_group" "brown1sg" {
  name = "brown1sg"
  description = "brown1 security group"
  vpc_id = aws_vpc.brown1.id

  tags = {
    Name = "brown1sg"
  }
}

resource "aws_security_group" "brown2sg" {
  name = "brown2sg"
  description = "brown2 security group"
  vpc_id = aws_vpc.brown2.id

  tags = {
    Name = "brown2sg"
  }
}

resource "aws_security_group" "brown3sg" {
  name = "brown3sg"
  description = "brown3 security group"
  vpc_id = aws_vpc.brown3.id

  tags = {
    Name = "brown3sg"
  }
}


# Create Security Group Rules
resource "aws_security_group_rule" "brown1in" {
  type = "ingress"
  from_port = -1
  protocol = "all"
  to_port  = -1
  security_group_id = aws_security_group.brown1sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "brown1eg" {
  type = "egress"
  from_port = -1
  protocol = "all"
  to_port  = -1
  security_group_id = aws_security_group.brown1sg.id
  cidr_blocks = ["0.0.0.0/0"]
}


resource "aws_security_group_rule" "brown2in" {
  type = "ingress"
  from_port = -1
  protocol = "all"
  to_port  = -1
  security_group_id = aws_security_group.brown2sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "brown2eg" {
  type = "egress"
  from_port = -1
  protocol = "all"
  to_port  = -1
  security_group_id = aws_security_group.brown2sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "brown3in" {
  type = "ingress"
  from_port = -1
  protocol = "all"
  to_port  = -1
  security_group_id = aws_security_group.brown3sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "brown3eg" {
  type = "egress"
  from_port = -1
  protocol = "all"
  to_port  = -1
  security_group_id = aws_security_group.brown3sg.id
  cidr_blocks = ["0.0.0.0/0"]
}

# create instances
resource "aws_instance" "web1" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.net1brown1.id
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.brown1sg.id
  ]

  key_name = "htduong01virgina"

  tags = {
    Name = "web1"
  }
}

resource "aws_instance" "web2" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.net1brown2.id
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.brown2sg.id
  ]

  key_name = "htduong01virgina"

  tags = {
    Name = "web2"

  }
}

resource "aws_instance" "web3" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.net1brown3.id
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.brown3sg.id
  ]

  key_name = "htduong01virgina"

  tags = {
    Name = "web3"

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

output "web3-private-ip" {
  value = aws_instance.web3.private_ip
}

output "web3-public-ip" {
  value = aws_instance.web3.public_ip
}

