output "ai_gateway_endpoint" {
  description = "HTTP API endpoint for the AI Gateway."
  value       = module.api_gateway.api_endpoint
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_client_id" {
  value = module.cognito.client_id
}


# ---------------------------------------------------------
# CLOUDWATCH DASHBOARD OUTPUT
# ---------------------------------------------------------

output "security_dashboard_name" {
  description = "CloudWatch dashboard for AI security monitoring."
  value       = module.cloudwatch.dashboard_name
}