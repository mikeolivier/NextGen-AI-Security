resource "aws_apigatewayv2_api" "ai_gateway" {
  name          = "${var.project}-ai-gateway"
  protocol_type = "HTTP"

  tags = var.common_tags
}

resource "aws_apigatewayv2_integration" "ai_agent" {
  api_id = aws_apigatewayv2_api.ai_gateway.id

  integration_type   = "AWS_PROXY"
  integration_uri    = "arn:aws:apigateway:${data.aws_region.current.region}:lambda:path/2015-03-31/functions/${data.aws_lambda_function.ai_agent.arn}/invocations"
  integration_method = "POST"

  payload_format_version = "2.0"
}


resource "aws_apigatewayv2_route" "invoke_agent" {
  api_id    = aws_apigatewayv2_api.ai_gateway.id
  route_key = "POST /agent"

  target = "integrations/${aws_apigatewayv2_integration.ai_agent.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}



resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.ai_gateway.id
  name   = "$default"

  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 10
    throttling_rate_limit  = 5
  }

  tags = var.common_tags
}

data "aws_region" "current" {}

data "aws_lambda_function" "ai_agent" {
  function_name = var.lambda_function_name
}


resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.ai_agent.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.ai_gateway.execution_arn}/*/*"
}


resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.ai_gateway.id
  authorizer_type  = "JWT"
  authorizer_uri   = null
  identity_sources = ["$request.header.Authorization"]
  name             = "${var.project}-cognito-authorizer"

  jwt_configuration {
    audience = [var.cognito_client_id]
    issuer   = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${var.cognito_user_pool_id}"
  }
}