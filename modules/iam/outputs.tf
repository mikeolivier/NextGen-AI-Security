output "ai_workload_role_arn" {
  description = "ARN of the AI workload IAM role."
  value       = aws_iam_role.ai_workload.arn
}