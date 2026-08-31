variable "project" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

variable "lambda_function_name" {
  type = string
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_client_id" {
  type = string
}