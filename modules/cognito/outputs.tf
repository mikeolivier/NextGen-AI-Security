output "user_pool_id" {
  value = aws_cognito_user_pool.ai_users.id
}

output "client_id" {
  value = aws_cognito_user_pool_client.ai_gateway.id
}