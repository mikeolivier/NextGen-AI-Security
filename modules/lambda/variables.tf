variable "project" {
  description = "Project name."
  type        = string
}

variable "common_tags" {
  description = "Standard project tags."
  type        = map(string)
}

variable "ai_workload_role_arn" {
  description = "IAM role used by the AI workload."
  type        = string
}


variable "bedrock_model_id" {
  description = "Bedrock foundation model used by the AI Agent."
  type        = string
}