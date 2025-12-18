# Kubernetes Manifests for Modular Learning Hub (MLH)

This directory contains Kubernetes manifests for deploying the MLH microservices platform.

## Directory Structure

```
k8s/
├── namespace.yaml          # MLH platform namespace
├── configmap.yaml          # Environment configuration
├── secrets.yaml            # Sensitive credentials (change before deploying!)
├── postgres.yaml           # PostgreSQL StatefulSet
├── redis.yaml              # Redis deployment
├── user-service.yaml       # User Service deployment + HPA
├── course-service.yaml     # Course Service deployment + HPA
├── enrollment-service.yaml # Enrollment Service deployment + HPA
├── payment-service.yaml    # Payment Service deployment + HPA
├── celery.yaml             # Celery worker and beat scheduler
├── ingress.yaml            # NGINX Ingress with TLS
└── README.md               # This file
```

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- NGINX Ingress Controller installed
- Cert-manager (optional, for TLS)

## Deployment

### 1. Create Namespace
```bash
kubectl apply -f namespace.yaml
```

### 2. Configure Secrets
**Important:** Edit `secrets.yaml` and change all passwords before deploying!

```bash
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml
```

### 3. Deploy Infrastructure
```bash
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
```

Wait for infrastructure to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n mlh-platform --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n mlh-platform --timeout=60s
```

### 4. Deploy Services
```bash
kubectl apply -f user-service.yaml
kubectl apply -f course-service.yaml
kubectl apply -f enrollment-service.yaml
kubectl apply -f payment-service.yaml
kubectl apply -f celery.yaml
```

### 5. Configure Ingress
```bash
kubectl apply -f ingress.yaml
```

## Verify Deployment

```bash
# Check all pods
kubectl get pods -n mlh-platform

# Check services
kubectl get svc -n mlh-platform

# Check HPA status
kubectl get hpa -n mlh-platform

# Check logs
kubectl logs -f deployment/user-service -n mlh-platform
```

## Scaling

The services are configured with Horizontal Pod Autoscalers (HPA):
- **User Service:** 2-10 replicas
- **Course Service:** 3-15 replicas (read-heavy)
- **Enrollment Service:** 2-10 replicas
- **Payment Service:** 2-10 replicas

Manual scaling:
```bash
kubectl scale deployment course-service --replicas=5 -n mlh-platform
```

## Clean Up

```bash
kubectl delete namespace mlh-platform
```
