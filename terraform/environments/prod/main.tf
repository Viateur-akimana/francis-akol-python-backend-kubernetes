terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    bucket         = "mlh-platform-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "mlh-platform-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "ModularLearningHub"
      Environment = "production"
      Owner       = "Francis-Akol"
      ManagedBy   = "Terraform"
    }
  }
}

provider "kubernetes" {
  host                   = module.compute.cluster_endpoint
  cluster_ca_certificate = base64decode(module.compute.cluster_ca_certificate)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.compute.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.compute.cluster_endpoint
    cluster_ca_certificate = base64decode(module.compute.cluster_ca_certificate)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.compute.cluster_name]
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# VARIABLES (Strictly defined, values are provided by terraform.tfvars)
# ---------------------------------------------------------------------------------------------------------------------

variable "region" {
  description = "AWS region"
  type        = string
}

variable "cluster_name" {
  description = "EKS Cluster name"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
}

variable "db_user" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# ---------------------------------------------------------------------------------------------------------------------
# MODULES
# ---------------------------------------------------------------------------------------------------------------------

module "networking" {
  source       = "../../modules/networking"
  cluster_name = var.cluster_name
  vpc_cidr     = var.vpc_cidr
  environment  = "production"
}

module "security" {
  source       = "../../modules/security"
  cluster_name = var.cluster_name
  environment  = "production"
  vpc_id       = module.networking.vpc_id
}

module "compute" {
  source              = "../../modules/compute"
  cluster_name        = var.cluster_name
  vpc_id              = module.networking.vpc_id
  private_subnets     = module.networking.private_subnets
  environment         = "production"
  spot_instance_types = ["t3.large", "c5.large"]
  kms_key_arn         = module.security.kms_key_arn
}

module "database" {
  source                  = "../../modules/database"
  vpc_id                  = module.networking.vpc_id
  private_subnets          = module.networking.private_subnets
  environment             = "production"
  db_name                 = "mlh_production"
  db_user                 = var.db_user
  db_password             = var.db_password
  allowed_security_groups = [module.security.node_sg_id]
}

module "gitops" {
  source       = "../../modules/gitops"
  cluster_name = module.compute.cluster_name
  environment  = "production"
}
