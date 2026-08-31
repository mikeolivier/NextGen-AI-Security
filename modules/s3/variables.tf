variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "common_tags" {
  description = "Standard tags applied to resources."
  type        = map(string)
}