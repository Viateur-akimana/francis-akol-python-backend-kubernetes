# Karpenter Module Main configuration

# ---------------------------------------------------------------------------------------------------------------------
# RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

# Karpenter Interruption Queue (for Spot termination handling)
resource "aws_sqs_queue" "karpenter_interruption" {
  name                      = "${var.cluster_name}-karpenter-interruption"
  message_retention_seconds = 300
}

# EventBridge rules for Karpenter
resource "aws_cloudwatch_event_rule" "interruption_rules" {
  for_each = {
    scheduled_change = "AWS Health Event"
    spot_interruption = "EC2 Spot Instance Interruption Warning"
    rebalance_recommendation = "EC2 Instance Rebalance Recommendation"
    instance_state_change = "EC2 Instance State-change Notification"
  }
  name        = "${var.cluster_name}-${each.key}"
  description = "Karpenter interruption rule for ${each.value}"
  event_pattern = jsonencode({
    source      = ["aws.ec2", "aws.health"]
    detail-type = [each.value]
  })
}

resource "aws_cloudwatch_event_target" "sqs_target" {
  for_each  = aws_cloudwatch_event_rule.interruption_rules
  rule      = each.value.name
  target_id = "KarpenterInterruptionQueueTarget"
  arn       = aws_sqs_queue.karpenter_interruption.arn
}

resource "aws_sqs_queue_policy" "karpenter_interruption" {
  queue_url = aws_sqs_queue.karpenter_interruption.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = ["events.amazonaws.com", "sqs.amazonaws.com"]
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.karpenter_interruption.arn
      }
    ]
  })
}

# Install Karpenter via Helm
resource "helm_release" "karpenter" {
  namespace        = "karpenter"
  create_namespace = true
  name             = "karpenter"
  repository       = "oci://public.ecr.aws/karpenter"
  chart            = "karpenter"
  version          = "1.0.1"

  set {
    name  = "settings.clusterName"
    value = var.cluster_name
  }

  set {
    name  = "settings.clusterEndpoint"
    value = var.cluster_endpoint
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = var.karpenter_iam_role_arn
  }

  set {
    name  = "settings.interruptionQueueName"
    value = aws_sqs_queue.karpenter_interruption.name
  }
}

# Karpenter NodePool and EC2NodeClass (Standard for Spot Application Pods)
# Note: Using kubernetes_manifest requires the CRDs to be present. 
# In a real environment, we would use a separate provisioner or a null_resource with kubectl.
resource "kubernetes_manifest" "karpenter_node_class" {
  manifest = {
    apiVersion = "karpenter.k8s.aws/v1beta1"
    kind       = "EC2NodeClass"
    metadata = {
      name = "default"
    }
    spec = {
      amiFamily = "AL2"
      role      = var.node_iam_role_name
      subnetSelectorTerms = [
        for s in var.private_subnets : { id = s }
      ]
      securityGroupSelectorTerms = [
        { tags = { "kubernetes.io/cluster/${var.cluster_name}" = "owned" } }
      ]
      tags = {
        "karpenter.sh/discovery" = var.cluster_name
      }
    }
  }
  depends_on = [helm_release.karpenter]
}

resource "kubernetes_manifest" "karpenter_node_pool" {
  manifest = {
    apiVersion = "karpenter.sh/v1beta1"
    kind       = "NodePool"
    metadata = {
      name = "default"
    }
    spec = {
      template = {
        spec = {
          nodeClassRef = {
            name = "default"
          }
          requirements = [
            { key = "karpenter.sh/capacity-type", operator = "In", values = ["spot"] },
            { key = "kubernetes.io/arch", operator = "In", values = ["amd64"] },
            { key = "karpenter.k8s.aws/instance-category", operator = "In", values = ["c", "m", "r"] },
            { key = "karpenter.k8s.aws/instance-generation", operator = "Gt", values = ["2"] }
          ]
        }
      }
      disruption = {
        consolidationPolicy = "WhenUnderutilized"
        expireAfter        = "720h"
      }
    }
  }
  depends_on = [kubernetes_manifest.karpenter_node_class]
}
