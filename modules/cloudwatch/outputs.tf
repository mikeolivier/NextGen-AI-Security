# ---------------------------------------------------------
# CloudWatch Dashboard Output
# ---------------------------------------------------------
#
# PURPOSE:
# Expose the dashboard name to the root Terraform module.
#
# WHY:
# The root outputs.tf can then display the dashboard name
# after Terraform creates the dashboard.
# ---------------------------------------------------------

output "dashboard_name" {
  description = "Name of the AI security CloudWatch dashboard."

  value = aws_cloudwatch_dashboard.security.dashboard_name
}
