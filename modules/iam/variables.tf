variable "project" {
  description = "Project name."
  type        = string
}

variable "common_tags" {
  description = "Common tags applied to IAM resources."
  type        = map(string)
}

variable "ai_data_bucket_arn" {
  description = "ARN of the approved AI data S3 bucket."
  type        = string
}