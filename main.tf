provider "aws" {
  region = var.aws_region
}


# =========================================================
# S3
# =========================================================

module "s3" {
  source = "./modules/s3"

  project_name = local.project
  common_tags  = local.common_tags
}


# =========================================================
# IAM
# =========================================================

module "iam" {
  source = "./modules/iam"

  project            = local.project
  common_tags        = local.common_tags
  ai_data_bucket_arn = module.s3.ai_data_bucket_arn
}


# =========================================================
# LAMBDA
# =========================================================

module "lambda" {
  source = "./modules/lambda"

  project              = local.project
  common_tags          = local.common_tags
  ai_workload_role_arn = module.iam.ai_workload_role_arn
  bedrock_model_id     = "ca.amazon.nova-lite-v1:0"
}


# =========================================================
# COGNITO
# =========================================================

module "cognito" {
  source = "./modules/cognito"

  project     = local.project
  common_tags = local.common_tags
}


# =========================================================
# API GATEWAY
# =========================================================

module "api_gateway" {
  source = "./modules/api_gateway"

  project              = local.project
  common_tags          = local.common_tags
  lambda_function_name = module.lambda.ai_agent_function_name
  cognito_user_pool_id = module.cognito.user_pool_id
  cognito_client_id    = module.cognito.client_id
}


# =========================================================
# SNS SECURITY ALERTS
# =========================================================
#
# Sends CloudWatch security alarm notifications by email.
#
# IMPORTANT:
# Replace YOUR_EMAIL_HERE with the email address that should
# receive security alerts.
#
# =========================================================

module "sns" {
  source = "./modules/sns"

  project     = local.project
  common_tags = local.common_tags
  alert_email = var.alert_email
}


# =========================================================
# CLOUDWATCH SECURITY MONITORING
# =========================================================

module "cloudwatch" {
  source = "./modules/cloudwatch"

  project     = local.project
  common_tags = local.common_tags

  log_group_name = "/aws/lambda/${module.lambda.ai_agent_function_name}"

  sns_topic_arn = module.sns.topic_arn
}


# ---------------------------------------------------------
# SNS SECURITY ALERTS
# ---------------------------------------------------------
#
# PURPOSE:
# Sends security alerts through Amazon SNS.
#
# WHY:
# CloudWatch alarms can notify us when the AI security
# gateway detects potentially sensitive activity.
# ---------------------------------------------------------

# module "sns" {
#   source = "./modules/sns"

#   project     = local.project
#   common_tags = local.common_tags

#   alert_email = var.alert_email
# }