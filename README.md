# Modular Learning Hub (MLH)

**Transform a monolithic LMS into a scalable Python microservices architecture**

[![CI Pipeline](https://img.shields.io/badge/CI-GitHub%20Actions-blue)](https://github.com/franakol/francis-akol-python-backend-assessment/actions)
[![Infrastructure](https://img.shields.io/badge/IaC-Terraform-623CE4)](https://www.terraform.io/)
[![Orchestration](https://img.shields.io/badge/EKS-AWS-orange)](https://aws.amazon.com/eks/)
[![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-green)](https://argoproj.github.io/argo-cd/)

---

## Project Overview

The Modular Learning Hub (MLH) is a modern, scalable Learning Management System (LMS) built using microservices architecture. This project demonstrates the migration from a monolithic application to a distributed system using Python, FastAPI, PostgreSQL, MongoDB, Redis, and Kubernetes.

### Key Features

- JWT-based Authentication with role-based access control (RBAC)
- Course Management with flexible content storage
- Student Enrollment with quota management
- Payment Processing with transaction integrity
- Redis Caching for high-performance reads
- Async Task Processing with Celery

---

## Architecture

### Microservices

| Service | Port | Description |
|---------|------|-------------|
| **User Service** | 8001 | Authentication, user management, RBAC |
| **Course Service** | 8002 | Course CRUD, content management, caching |
| **Enrollment Service** | 8003 | Student enrollments, quota enforcement |
| **Payment Service** | 8004 | Payment processing, transaction management |

### Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Databases:** PostgreSQL 15, MongoDB 6, Redis 7
- **Message Queue:** Celery + Redis/RabbitMQ
- **Containerization:** Docker, Docker Compose
- **Orchestration:** AWS EKS (Kubernetes)
- **Infrastructure:** Terraform (Modular 3-Tier)
- **GitOps:** ArgoCD
- **Monitoring:** Prometheus, Grafana, Loguru
- **Testing:** Pytest, Locust
- **CI/CD:** GitHub Actions

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                       │
│         (Web App, Mobile App, Admin Panel)          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              API Gateway (ALB)                       │
└────────────────────┬────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┬────────────────┐
     │               │               │                │
┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐    ┌─────▼─────┐
│  User   │    │  Course   │   │Enrollment│    │  Payment  │
│ Service │    │  Service  │   │ Service  │    │  Service  │
│  :8001  │    │   :8002   │   │  :8003   │    │   :8004   │
└────┬────┘    └─────┬─────┘    └────┬─────┘    └─────┬─────┘
     │               │               │                │
     └───────────────┼───────────────┴────────────────┘
                     │
     ┌───────────────┼───────────────┬────────────────┐
     │               │               │                │
┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐    ┌─────▼─────┐
│ Amazon  │    │  MongoDB  │   │  Redis  │    │  Celery   │
│ RDS (PG)│    │  :27017   │   │  :6379  │    │  Worker   │
└──────────┘   └───────────┘   └─────────┘    └───────────┘
```

---

## Deployment & Infrastructure

### 1. Local Development (Docker Compose)

```bash
# Clone the repository
git clone git@github.com:franakol/francis-akol-python-backend-assessment.git
cd francis-akol-python-backend-assessment

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d
```

### 2. Cloud Infrastructure (AWS EKS)

The infrastructure is orchestrated using a **Three-Tier Modular Terraform** architecture located in [`terraform/modules/`](terraform/modules/):
- **Networking:** Multi-AZ VPC with Public/Private subnets.
- **Security:** Security Group Hierarchy (Internet ➡ ALB ➡ EKS Nodes ➡ RDS) and KMS Encryption.
- **Compute:** EKS Managed Spot Node Groups.
- **Database:** Amazon RDS for high availability.

#### To deploy into Staging or Production:
```bash
# 1. Initialize S3 Backend
cd terraform/environments/staging
terraform init

# 2. Plan and Apply
terraform apply -var-file="terraform.tfvars"
```

### 3. GitOps Workflow (ArgoCD)

Deployment to EKS is fully automated. Simply push changes to the [`k8s/`](k8s/) directory, and **ArgoCD** will automatically synchronize the state to the live cluster.

---

## Testing Strategy

### Test Coverage

| Service | Unit Tests | Integration Tests | API Tests | Coverage |
| --- | --- | --- | --- | --- |
| User Service | Yes | Yes | Yes | 85%+ |
| Course Service | Yes | Yes | Yes | 82%+ |
| Enrollment Service | Yes | Yes | Yes | 88%+ |
| Payment Service | Yes | Yes | Yes | 90%+ |

---

## Monitoring & Observability

- **Metrics (Prometheus):** Accessible at http://localhost:9090 (local) or via ALB (cloud).
- **Dashboards (Grafana):** Accessible at http://localhost:3000 (local).
- **Logging:** Structured logs via Loguru, integrated with CloudWatch.

---

## Design Decisions & Trade-offs

- **Microservices:** Benefits of scale out-weigh network complexity. 
- **Database per Service:** Ensures data encapsulation and tech flexibility.
- **Security Hierarchy:** Private subnets reachable only via BAL.

---

## Documentation Index

- [High Level Design (HLD)](file:///home/viateur/francis-akol-python-backend-kubernetes/docs/architecture/HLD.md)
- [Infrastructure Guide](file:///home/viateur/francis-akol-python-backend-kubernetes/docs/deployment/infrastructure-guide.md)
- [Changelog](file:///home/viateur/francis-akol-python-backend-kubernetes/CHANGELOG.md)

---

**Author:** Francis Akol  
**Status:** Production Ready EKS Infrastructure  
Built with modern DevOps practices.