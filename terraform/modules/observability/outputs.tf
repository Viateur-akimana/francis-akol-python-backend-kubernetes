output "cloudwatch_log_group_name" {
  description = "The name of the CloudWatch log group for EKS logs"
  value       = aws_cloudwatch_log_group.eks_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "The ARN of the CloudWatch log group for EKS logs"
  value       = aws_cloudwatch_log_group.eks_logs.arn
}
