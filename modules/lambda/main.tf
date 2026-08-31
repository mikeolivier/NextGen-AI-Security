data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/handler.py"
  output_path = "${path.module}/src/handler.zip"
}

resource "aws_lambda_function" "ai_agent" {
  function_name = "${var.project}-ai-agent"

  role = var.ai_workload_role_arn

  runtime = "python3.12"
  handler = "handler.handler"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  timeout = 30

  environment {
    variables = {
      BEDROCK_MODEL_ID = var.bedrock_model_id
    }
  }

  tags = var.common_tags
}


resource "aws_cloudwatch_log_group" "ai_agent" {
  name              = "/aws/lambda/${aws_lambda_function.ai_agent.function_name}"
  retention_in_days = 30

  tags = var.common_tags
}