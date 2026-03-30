# Observability Module Main configuration

# ---------------------------------------------------------------------------------------------------------------------
# IAM & LOGGING
# ---------------------------------------------------------------------------------------------------------------------

# IAM Role for Fluent-bit (Log Shipping to CloudWatch)
resource "aws_iam_role" "fluent_bit" {
  name = "${var.cluster_name}-fluent-bit-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}:sub" : "system:serviceaccount:logging:fluent-bit"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fluent_bit_cloudwatch" {
  role       = aws_iam_role.fluent_bit.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# CloudWatch Log Group for EKS Logs
resource "aws_cloudwatch_log_group" "eks_logs" {
  name              = "/aws/eks/${var.cluster_name}/logs"
  retention_in_days = 30
}

# ---------------------------------------------------------------------------------------------------------------------
# HELM RELEASES
# ---------------------------------------------------------------------------------------------------------------------

# Prometheus & Grafana (Kube-Prometheus-Stack)
resource "helm_release" "prometheus_stack" {
  name             = "prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  version          = "55.0.0"

  values = [
    yamlencode({
      grafana = {
        adminPassword = "admin"
      }
      prometheus = {
        prometheusSpec = {
          storageSpec = {
            volumeClaimTemplate = {
              spec = {
                resources = {
                  requests = {
                    storage = "10Gi"
                  }
                }
              }
            }
          }
        }
      }
    })
  ]
}

# Fluent-bit (AWS version)
resource "helm_release" "fluent_bit" {
  name             = "fluent-bit"
  namespace        = "logging"
  create_namespace = true
  repository       = "https://aws.github.io/eks-charts"
  chart            = "aws-for-fluent-bit"
  version          = "0.1.31"

  values = [
    yamlencode({
      serviceAccount = {
        annotations = {
          "eks.amazonaws.com/role-arn" = aws_iam_role.fluent_bit.arn
        }
      }
      cloudWatch = {
        region          = data.aws_region.current.name
        logGroupName    = aws_cloudwatch_log_group.eks_logs.name
        autoCreateGroup = "false"
      }
    })
  ]
}

# OpenSearch (Elasticsearch backend for EFK)
resource "helm_release" "opensearch" {
  name             = "opensearch"
  namespace        = "logging"
  repository       = "https://opensearch-project.github.io/helm-charts/"
  chart            = "opensearch"
  version          = "2.16.0"

  values = [
    yamlencode({
      singleNode = true
    })
  ]
}

# OpenSearch Dashboards (Kibana UI)
resource "helm_release" "opensearch_dashboards" {
  name             = "opensearch-dashboards"
  namespace        = "logging"
  repository       = "https://opensearch-project.github.io/helm-charts/"
  chart            = "opensearch-dashboards"
  version          = "2.14.0"

  depends_on = [helm_release.opensearch]
}

# Jaeger (Distributed Tracing)
resource "helm_release" "jaeger" {
  name             = "jaeger"
  namespace        = "monitoring"
  repository       = "https://jaegertracing.github.io/helm-charts"
  chart            = "jaeger"
  version          = "0.71.0"

  values = [
    yamlencode({
      allInOne = {
        enabled = true
      }
      storage = {
        type = "elasticsearch"
        elasticsearch = {
          host = "opensearch-cluster-master.logging.svc.cluster.local"
        }
      }
    })
  ]
}

# ---------------------------------------------------------------------------------------------------------------------
# DATA SOURCES
# ---------------------------------------------------------------------------------------------------------------------

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_eks_cluster" "cluster" {
  name = var.cluster_name
}
