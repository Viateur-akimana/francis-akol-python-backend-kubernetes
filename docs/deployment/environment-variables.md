# Environment Variables

This document describes all environment variables used by the MLH platform.

## Application Variables

| Variable | Description |
| --- | --- |
| `ENVIRONMENT` | Environment name (staging, production) |
| `DEBUG` | Enable debug mode (false in production) |
| `DATABASE_URL` | RDS PostgreSQL connection string |
| `REDIS_URL` | Redis connection URL |
| `JWT_SECRET_KEY` | JWT signing key (Min 32 chars) |
| `JWT_ALGORITHM` | JWT algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry (30) |

## Cloud Infrastructure Variables

Infrastructure variables are managed via Terraform `TF_VAR_` environment variables:

| Variable | Description | Source |
| --- | --- | --- |
| `TF_VAR_db_password` | RDS Master Password | GitHub Secrets |
| `TF_VAR_kms_key_arn` | EKS Encryption Key | Terraform Output |
| `TF_VAR_vpc_id` | AWS VPC ID | Terraform Output |

## Security Strategy

The production environment uses a multi-layered security strategy for secrets:

1. **GitHub Secrets:** Used by the CI/CD pipeline to inject sensitive variables into the Terraform apply phase.
2. **KMS & IRSA:** The EKS cluster is configured with KMS for at-rest encryption of Kubernetes Secrets.
3. **IAM Roles for Service Accounts (IRSA):** Pods are assigned specific IAM roles to securely access AWS services like RDS or KMS without using long-lived credentials.

## Generating Secrets

To generate a secure JWT secret:

```bash
openssl rand -hex 32
```

## Production Deployment Checklist

- Ensure `DB_PASSWORD` is set in GitHub Repository Secrets.
- Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` have the required permissions.
- Use different `JWT_SECRET_KEY` for each environment.

---

Last updated: March 30, 2026.
