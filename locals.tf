locals {
  project     = "nextgen-ai-security"
  environment = "dev"

  common_tags = {
    Project     = local.project
    Environment = local.environment
    ManagedBy   = "Terraform"
    Owner       = "AI-Security-Team"
  }
}