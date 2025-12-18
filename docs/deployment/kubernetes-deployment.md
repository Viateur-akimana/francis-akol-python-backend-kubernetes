# Kubernetes Deployment Guide

This guide covers deploying the MLH platform to Kubernetes.

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- NGINX Ingress Controller
- Cert-manager (for TLS)

## Deployment Steps

### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Configure Secrets

**Important:** Edit `k8s/secrets.yaml` with production credentials before deploying.

```bash
# Edit secrets first!
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
```

### 3. Deploy Infrastructure
```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n mlh-platform --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n mlh-platform --timeout=60s
```

### 4. Deploy Services
```bash
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/course-service.yaml
kubectl apply -f k8s/enrollment-service.yaml
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/celery.yaml
```

### 5. Configure Ingress
```bash
kubectl apply -f k8s/ingress.yaml
```

## Verification

```bash
# Check all pods
kubectl get pods -n mlh-platform

# Check services
kubectl get svc -n mlh-platform

# Check HPA
kubectl get hpa -n mlh-platform

# View logs
kubectl logs -f deployment/user-service -n mlh-platform
```

## Scaling

### Automatic Scaling (HPA)
Services scale automatically based on CPU (70% threshold):
- User Service: 2-10 replicas
- Course Service: 3-15 replicas
- Enrollment Service: 2-10 replicas
- Payment Service: 2-10 replicas

### Manual Scaling
```bash
kubectl scale deployment course-service --replicas=5 -n mlh-platform
```

## Database Migrations

Run migrations as a Kubernetes Job:
```bash
kubectl run migration --image=mlh-user-service:latest \
  --restart=Never \
  -n mlh-platform \
  -- alembic upgrade head
```

## Monitoring

### Health Checks
- Liveness: `GET /health`
- Readiness: `GET /ready`

### Logs
```bash
kubectl logs -f deployment/user-service -n mlh-platform
```

## Rollback

```bash
# View revision history
kubectl rollout history deployment/user-service -n mlh-platform

# Rollback to previous version
kubectl rollout undo deployment/user-service -n mlh-platform

# Rollback to specific revision
kubectl rollout undo deployment/user-service --to-revision=2 -n mlh-platform
```

## Cleanup

```bash
kubectl delete namespace mlh-platform
```
