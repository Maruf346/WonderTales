variable "aws_profile" {
  description = "AWS CLI profile name configured locally"
  default     = "wondertales"
}

variable "region" {
  description = "AWS region"
  default     = "eu-north-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "ami" {
  description = "Ubuntu AMI ID"
  default     = "ami-0c33fcb753a7176f6" # Standard Ubuntu 22.04 LTS in eu-north-1
}

variable "bucket_name" {
  description = "S3 bucket name"
  default     = "wonder-tales-bucket"
}

variable "ec2_name" {
  description = "Name tag for EC2 instance"
  default     = "wondertales_server"
}

variable "db_username" {
  description = "RDS Postgres username"
  default     = "wondertales_db"
}

variable "db_password" {
  description = "RDS Postgres password"
  sensitive   = true
  default     = "wondertales_db_password"
}



