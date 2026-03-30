# CI/CD Pipeline Guide

This document describes the CI/CD pipeline configuration for the MLH platform.

## Overview

The platform uses GitHub Actions for continuous integration and deployment. The pipeline is split into CI (Quality & Tests) and CD (Infrastructure & Application Deployment).

## CI Pipeline (.github/workflows/ci.yml)

### Triggers
- Push to: `main`, `feature/*`, `fix/*`
- Pull requests to: `main`

### Workflow Steps
1. **Code Quality Checks:**
   - **Black:** Code formatting check.
   - **isort:** Import sorting check.
   - **flake8:** Linting.
   - **mypy:** Type checking.
2. **Security Scan:**
   - **Bandit:** Static security analysis for Python code.
   - **Trivy:** Container image scanning for vulnerabilities.
3. **Automated Testing:**
   - Runs unit and integration tests per service.
   - Generates coverage reports.

## CD Pipeline (.github/workflows/cd.yml)

The CD pipeline manages the building of artifacts and the provisioning of infrastructure.

### Workflow Steps
1. **Build and Push:**
   - Builds Docker images for all microservices.
   - Pushes images to GitHub Container Registry (GHCR).
2. **Infrastructure Provisioning:**
   - Uses Terraform to provision AWS EKS, RDS, and Networking.
   - Manages environments (Staging/Production).
   - Injects secrets via `TF_VAR_` environment variables.

## Deployment Strategy

1. **GitOps (ArgoCD):**
   - The cluster is synchronized with the `k8s/` directory.
   - Any commit to the `k8s/` manifests triggers an automatic rollout.
2. **Staging & Production:**
   - Commits to `main` auto-deploy to Staging.
   - Production deployments are triggered manually via GitHub Actions with approval gates.

---

Last updated: March 30, 2026.
