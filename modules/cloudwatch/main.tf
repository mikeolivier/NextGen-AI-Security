# ---------------------------------------------------------
# CLOUDWATCH SECURITY MONITORING
# ---------------------------------------------------------
#
# PURPOSE:
# Creates the CloudWatch dashboard and security alarms
# for the AI Security Gateway.
#
# SECURITY FLOW:
#
#   Lambda Security Event
#          |
#          v
#   CloudWatch Metric
#          |
#          v
#   CloudWatch Alarm
#          |
#          v
#          SNS
#          |
#          v
#      Email Alert
#
# ---------------------------------------------------------


# =========================================================
# CLOUDWATCH SECURITY DASHBOARD
# =========================================================

resource "aws_cloudwatch_dashboard" "security" {

  dashboard_name = "${var.project}-security-dashboard"

  dashboard_body = jsonencode({

    widgets = [

      # ---------------------------------------------------
      # WIDGET 1 — SECURITY EVENTS
      # ---------------------------------------------------

      {
        type   = "log"
        x      = 0
        y      = 0
        width  = 24
        height = 6

        properties = {
          title  = "AI Security Events"
          region = "ca-central-1"

          query = <<-EOT
            SOURCE '${var.log_group_name}'
            | fields @timestamp, event, control, action, reason, request_id
            | filter event = "security_event"
            | sort @timestamp desc
            | limit 100
          EOT

          view = "table"
        }
      },


      # ---------------------------------------------------
      # WIDGET 2 — ALLOWED REQUESTS
      # ---------------------------------------------------

      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 8
        height = 6

        properties = {
          title  = "Allowed Requests"
          region = "ca-central-1"

          query = <<-EOT
            SOURCE '${var.log_group_name}'
            | fields @timestamp, control, action, reason
            | filter event = "security_event"
            | filter action = "ALLOW"
            | stats count() as allowed_requests
          EOT

          view = "table"
        }
      },


      # ---------------------------------------------------
      # WIDGET 3 — DLP BLOCKS
      # ---------------------------------------------------

      {
        type   = "log"
        x      = 8
        y      = 6
        width  = 8
        height = 6

        properties = {
          title  = "DLP Blocks"
          region = "ca-central-1"

          query = <<-EOT
            SOURCE '${var.log_group_name}'
            | fields @timestamp, control, action, reason
            | filter event = "security_event"
            | filter control = "dlp"
            | filter action = "BLOCK"
            | stats count() as dlp_blocks
          EOT

          view = "table"
        }
      },


      # ---------------------------------------------------
      # WIDGET 4 — PROMPT INJECTION BLOCKS
      # ---------------------------------------------------

      {
        type   = "log"
        x      = 16
        y      = 6
        width  = 8
        height = 6

        properties = {
          title  = "Prompt Injection Blocks"
          region = "ca-central-1"

          query = <<-EOT
            SOURCE '${var.log_group_name}'
            | fields @timestamp, control, action, reason
            | filter event = "security_event"
            | filter control = "prompt_injection"
            | filter action = "BLOCK"
            | stats count() as injection_blocks
          EOT

          view = "table"
        }
      },


      # ---------------------------------------------------
      # WIDGET 5 — SECURITY ACTIVITY OVER TIME
      # ---------------------------------------------------

      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 8

        properties = {
          title  = "Security Events Over Time"
          region = "ca-central-1"

          query = <<-EOT
            SOURCE '${var.log_group_name}'
            | fields @timestamp, control, action
            | filter event = "security_event"
            | stats count() by bin(5m), action
          EOT

          view = "bar"
        }
      }

    ]
  })
}


# =========================================================
# DLP SECURITY ALARM
# =========================================================
#
# WHAT:
# Detects when the DLP security control blocks a request.
#
# WHY:
# A DLP block can indicate that sensitive information was
# submitted to the AI gateway.
#
# =========================================================

resource "aws_cloudwatch_metric_alarm" "dlp_block" {

  alarm_name = "${var.project}-DLP-Block"

  alarm_description = "Alerts when the AI security gateway blocks a request containing potentially sensitive data."

  namespace   = "NextGen-AI-Security"
  metric_name = "SecurityEvents"

  dimensions = {
    Control = "dlp"
    Action  = "BLOCK"
  }

  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  alarm_actions = [
    var.sns_topic_arn
  ]

  tags = var.common_tags
}


# =========================================================
# PROMPT INJECTION SECURITY ALARM
# =========================================================
#
# WHAT:
# Detects when the prompt-injection control blocks a request.
#
# WHY:
# Prompt injection attempts can indicate malicious attempts
# to manipulate the AI system or bypass security controls.
#
# =========================================================

resource "aws_cloudwatch_metric_alarm" "prompt_injection_block" {

  alarm_name = "${var.project}-Prompt-Injection-Block"

  alarm_description = "Alerts when the AI security gateway blocks a potential prompt injection attempt."

  namespace   = "NextGen-AI-Security"
  metric_name = "SecurityEvents"

  dimensions = {
    Control = "prompt_injection"
    Action  = "BLOCK"
  }

  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  alarm_actions = [
    var.sns_topic_arn
  ]

  tags = var.common_tags
}
