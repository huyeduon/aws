
variable "access_key" {}
variable "secret_key" {}
variable "region" {
    default = "us-west-2"
}

variable "pAvailabilityZone" {
    type = string
    default = "us-west-2a"
}

variable "pKeyName" {
    type = string
    default = "htduong03oregon"
}

variable "pInfraVPCPool" {
    type = string
    default = "10.99.0.0/24"
}

variable "pFabricName" {
    type = string
    default = "capic"
}

variable "pInstanceType" {
    type = string
    default = "m5.2xlarge"
}

variable "pExtNw" {
    type = string
    default = "0.0.0.0/0"
}

variable "pPassword" {
    type = string
    default = "123Cisco123!"
}

variable "pConfirmPassword" {
    type = string
    default = "123Cisco123!"
}
