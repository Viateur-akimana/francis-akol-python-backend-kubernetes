output "karpenter_interruption_queue_arn" {
  description = "The ARN of the Karpenter interruption SQS queue"
  value       = aws_sqs_queue.karpenter_interruption.arn
}

output "karpenter_interruption_queue_name" {
  description = "The name of the Karpenter interruption SQS queue"
  value       = aws_sqs_queue.karpenter_interruption.name
}
