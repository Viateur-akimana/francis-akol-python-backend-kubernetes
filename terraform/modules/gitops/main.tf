# ---------------------------------------------------------------------------------------------------------------------
# VARIABLES
# ---------------------------------------------------------------------------------------------------------------------

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# ---------------------------------------------------------------------------------------------------------------------
# RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true
  version          = "5.51.6"

  values = [
    <<-EOT
    server:
      extraArgs:
        - --insecure
      ingress:
        enabled: true
        ingressClassName: alb
        annotations:
          alb.ingress.kubernetes.io/scheme: internet-facing
          alb.ingress.kubernetes.io/target-type: ip
        hosts:
          - argocd.${var.environment}.mlh.example.com
    EOT
  ]
}

# ---------------------------------------------------------------------------------------------------------------------
# OUTPUTS
# ---------------------------------------------------------------------------------------------------------------------

output "argocd_server_host" {
  description = "The DNS host assigned to the ArgoCD server"
  value       = "argocd.${var.environment}.mlh.example.com"
}
