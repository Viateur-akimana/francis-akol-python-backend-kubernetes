# Deployment Strategies Guide

This document explains how to use the implemented **Blue-Green** deployment strategy for the Modular Learning Hub.

## 1. Blue-Green Strategy Overview
Blue-Green deployment is a technique that reduces downtime and risk by running two identical production environments, only one of which (the "Blue" environment) is live at a time. The "Green" environment is where the new version is tested before switching traffic.

### Advantages
- **Zero Downtime:** Traffic switch happens instantly.
- **Instant Rollback:** If the new version (Green) fails, traffic is immediately pointed back to the stable version (Blue).
- **Reduced Risk:** Testing happens in a real production-like environment before any users see it.

## 2. Implementing a Rollout
To use the Blue-Green strategy, you must use a `Rollout` resource instead of a standard `Deployment`.

### Example Rollout Manifest (User Service)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: mlh-user-service:v2.0.0
        ports:
        - containerPort: 8000
  strategy:
    blueGreen:
      # The active service points to the "stable" version
      activeService: user-service-active
      # The preview service points to the "new/testing" version
      previewService: user-service-preview
      # Automatically promote to active after successful analysis (optional)
      autoPromotionEnabled: false
```

## 3. Promoting a Release
Once you have verified the "Green" environment is healthy via the `previewService`, you can promote the rollout via the ArgoCD UI or the CLI:

```bash
kubectl argo rollouts promote user-service -n staging
```

## 4. Troubleshooting
If the rollout hangs or fails:
- Check the Rollout status: `kubectl argo rollouts get rollout user-service`
- Check logs: `kubectl logs -l app=user-service`
- Abort and Rollback: `kubectl argo rollouts abort user-service`
