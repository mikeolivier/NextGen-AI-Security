output "ai_data_bucket_arn" {
  description = "ARN of the AI data S3 bucket."
  value       = aws_s3_bucket.ai_data.arn
}