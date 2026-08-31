resource "aws_iam_role" "ai_workload" {
  name = "${var.project}-ai-workload-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy" "ai_s3_read" {
  name = "${var.project}-ai-s3-read"

  role = aws_iam_role.ai_workload.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject"
        ]

        Resource = "${var.ai_data_bucket_arn}/*"
      }
    ]
  })
}



resource "aws_iam_role_policy" "ai_bedrock_invoke" {
  name = "${var.project}-ai-bedrock-invoke"

  role = aws_iam_role.ai_workload.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "bedrock:InvokeModel"
        ]

        Resource = "*"
      }
    ]
  })
}



resource "aws_iam_role_policy" "ai_cloudwatch_logs" {
  name = "${var.project}-ai-cloudwatch-logs"

  role = aws_iam_role.ai_workload.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]

        Resource = "arn:aws:logs:*:*:log-group:/aws/lambda/*:*"
      }
    ]
  })
}


# ---------------------------------------------------------
# CloudWatch Metrics Permission
# ---------------------------------------------------------
# This allows the Lambda AI security agent to publish
# custom security metrics to Amazon CloudWatch.
#
# Why do we need this?
# Our security dashboard reads metrics such as:
# - Allowed requests
# - DLP blocks
# - Prompt-injection blocks
#
# Without this permission, Lambda can write logs but
# cannot publish custom metrics.
# ---------------------------------------------------------

resource "aws_iam_role_policy" "ai_cloudwatch_metrics" {
  name = "${var.project}-ai-cloudwatch-metrics"

  role = aws_iam_role.ai_workload.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "cloudwatch:PutMetricData"
        ]

        # PutMetricData does not support resource-level
        # permissions, so CloudWatch requires "*".
        Resource = "*"
      }
    ]
  })
}