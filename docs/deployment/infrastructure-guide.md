# Infrastructure Guide

This document describes the AWS Cloud Infrastructure for the Modular Learning Hub (MLH).

## Architecture Overview

The infrastructure uses a modular 3-tier Terraform design. It is partitioned into functional modules to ensure isolation and reusability.

### Core Modules

1. **Networking**
   - VPC with multi-AZ support.
   - Public subnets for Application Load Balancers (ALB).
   - Private subnets for EKS Worker Nodes and RDS.
   - NAT Gateway for outbound traffic from private resources.

2. **Security**
   - **KMS:** Dedicated master key for EKS secret encryption.
   - **Security Groups:** Implements a zero-trust flow:
     - `alb_sg`: Public HTTP/HTTPS access.
     - `node_sg`: Restricted to traffic from `alb_sg`.
     - `database_sg`: Restricted to traffic from `node_sg`.

3. **Compute (EKS)**
   - Managed EKS Cluster.
   - Managed Node Groups using EC2 Spot Instances for cost efficiency.
   - Essential add-ons: EBS CSI Driver, Metrics-Server (for HPA).

4. **Database (RDS)**
   - Amazon RDS PostgreSQL.
   - High availability (Multi-AZ) in Production.
   - Single-AZ in Staging.

5. **GitOps**
   - ArgoCD installed via Helm.
   - Monitors the `k8s/` directory for automated state synchronization.

---

## Environment Management

Infrastructure is separated into distinct environments:

- **Staging:** `terraform/environments/staging/`
- **Production:** `terraform/environments/prod/`

### Variable Management

Configuration is handled via `terraform.tfvars` files in each environment directory.
Sensitive data (e.g., `db_password`) must be provided as environment variables `TF_VAR_db_password` to avoid hardcoding.

---

## State Management

Remote state is stored in Amazon S3 with state locking via DynamoDB.
Configuration is in `backend.tf` within each environment.

---

## Deployment Process

1. Authenticate with AWS CLI.
2. Navigate to the environment directory.
3. Run `terraform init`.
4. Run `terraform plan -var-file="terraform.tfvars"`.
5. Run `terraform apply -var-file="terraform.tfvars"`.

---

Last updated: March 30, 2026.
