# **Pull Request: EKS GitOps Migration** 🏗️

## **Summary**
**EKS GitOps Migration and Hardening**

## **Description**
This PR migrates the **Modular Learning Hub** to a production-ready **AWS EKS** architecture using a robust **GitOps (ArgoCD)** workflow. The infrastructure has been modularized and hardened with a comprehensive **DevSecOps suite** in the CI/CD pipeline.

---

### 🏛️ **Architecture & Infrastructure (Terraform)**
- **Three-Tier Modular Design:** Refactor of networking, security, compute, database, and gitops into standalone modules.
- **Cost Optimization:** EKS nodes configured with **Spot Instances** for maximum efficiency.
- **High Availability:** Transitioned to **Multi-AZ RDS** for production databases.
- **KMS Encryption:** Configured AWS KMS for EKS secrets encryption at rest.

### 🛡️ **DevSecOps Security Suite**
Integrated the following automated scanning tools into the CI pipeline:
- **Trivy:** Image vulnerability scanning (CVEs).
- **Checkov:** IaC security and compliance scanning.
- **Kube-linter:** Managed manifest security and best practices Audit.
- **Gitleaks:** Secret detection and prevention.
- **Hadolint:** Dockerfile best-practice enforcement.

### 🔄 **GitOps & Pipeline Logic**
- **ArgoCD Automation:** Syncs `k8s/` manifests automatically to the EKS cluster.
- **Environment Management:** Dynamic configuration for `staging` and `production` via separate `.tfvars`.
- **Quality Gate:** Standardized code formatting across all services via **Black**.

---

## **Checklist**
- [x] Terraform modules validated and planned.
- [x] All microservices scan clean (Trivy/Hadolint).
- [x] No sensitive secrets committed (Gitleaks verified).
- [x] Environment-specific variables injected securely.

## **Related Issues**
Closes Milestone 8: EKS/GitOps Migration.
