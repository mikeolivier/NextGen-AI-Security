variable "aws_region" {
  description = "AWS region where the NextGen platform will be deployed."
  type        = string
  default     = "ca-central-1"
}

variable "alert_email" {
  description = "Email address for AI security alerts."
  type        = string
}