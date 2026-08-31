resource "aws_cognito_user_pool" "ai_users" {
  name = "${var.project}-users"

  tags = var.common_tags
}

resource "aws_cognito_user_pool_client" "ai_gateway" {
  name         = "${var.project}-gateway-client"
  user_pool_id = aws_cognito_user_pool.ai_users.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

resource "aws_cognito_user_pool_domain" "ai_gateway" {
  domain       = "${var.project}-auth"
  user_pool_id = aws_cognito_user_pool.ai_users.id
}