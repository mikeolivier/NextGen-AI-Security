resource "aws_sns_topic" "security_alerts" {
  name = "${var.project}-security-alerts"

  tags = var.common_tags
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
