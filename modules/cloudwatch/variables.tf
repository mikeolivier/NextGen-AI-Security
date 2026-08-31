# ---------------------------------------------------------
# CloudWatch Dashboard Variables
# ---------------------------------------------------------

variable "project" {
  description = "Project name used for CloudWatch resources."
  type        = string
}

variable "common_tags" {
  description = "Common tags for CloudWatch resources."
  type        = map(string)
}

variable "log_group_name" {
  description = "CloudWatch log group containing AI security events."
  type        = string
}

# ---------------------------------------------------------
# SNS SECURITY ALERTS
# ---------------------------------------------------------

variable "sns_topic_arn" {
  description = "SNS topic ARN used for CloudWatch security alarm notifications."
  type        = string
}
