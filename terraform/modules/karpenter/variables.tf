variable "cluster_name" {
  description = "EKS Cluster name"
  type        = string
}

variable "cluster_endpoint" {
  description = "EKS Cluster endpoint"
  type        = string
}

variable "karpenter_iam_role_arn" {
  description = "IAM Role ARN for Karpenter Controller"
  type        = string
}

variable "node_iam_role_name" {
  description = "IAM Role name for EKS Nodes"
  type        = string
}

variable "private_subnets" {
  description = "Private Subnet IDs"
  type        = list(string)
}
