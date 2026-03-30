# Observability Stack Guide

This document outlines the full observability suite implemented for the Modular Learning Hub EKS infrastructure. The stack follows the three pillars of observability: Metrics, Logging, and Tracing.

## 1. Metrics (Monitoring)
**Tool:** Kube-Prometheus-Stack (Prometheus & Grafana)

The monitoring layer provides real-time visibility into the health and performance of the EKS cluster, nodes, and individual microservices.

### Key Features
- **Prometheus:** Collects time-series metrics from Kubernetes components and application endpoints.
- **Grafana:** Provides visual dashboards. Includes built-in dashboards for Compute Resources (Cluster/Node/Pod) and Networking.
- **Alertmanager:** Configurable to send notifications (Slack/Email) based on threshold breaches (e.g., High CPU usage).

### How to Access
```bash
# Port-forward to Grafana UI
kubectl port-forward svc/prometheus-stack-grafana -n monitoring 3000:80
# Credentials: admin / [As configured in Terraform]
```

## 2. Logging (EFK)
**Tools:** OpenSearch, Fluent-bit, OpenSearch Dashboards (Kibana)

The logging layer automates the collection, indexing, and visualization of all container logs produced by the microservices.

### Implementation Details
- **Fluent-bit:** A lightweight daemonset that scrapes logs from `/var/log/containers` on each node and ships them to both OpenSearch and Amazon CloudWatch.
- **OpenSearch:** The storage and search engine for logs, configured in a single-node mode for cost-efficiency.
- **OpenSearch Dashboards:** The web interface for searching and filtering logs.

### Backup Strategy
Logs are multi-routed to **Amazon CloudWatch Logs** (`/aws/eks/[cluster-name]/logs`) for 30-day retention even if the in-cluster OpenSearch instance is scaled down.

## 3. Distributed Tracing
**Tool:** Jaeger

Jaeger provides end-to-end tracing for requests as they travel through the MLH microservices (User -> Course -> Enrollment -> Payment).

### Configuration
- **Storage Backend:** OpenSearch (Shared with the logging stack for reduced overhead).
- **Collector:** Receives spans from the application-level OpenTelemetry/Jaeger clients.
- **Query UI:** For visualizing request flows and identifying latency bottlenecks.

### How to Access
```bash
# Port-forward to Jaeger UI
kubectl port-forward svc/jaeger-query -n monitoring 16686:16686
```

## 4. Integration & Security
- **IAM Roles for Service Accounts (IRSA):** All observability components use fine-grained IAM roles to interact with AWS services (CloudWatch/KMS) rather than node-level permissions.
- **Encryption:** OpenSearch and Prometheus storage volumes are encrypted at rest using the cluster's KMS key.
