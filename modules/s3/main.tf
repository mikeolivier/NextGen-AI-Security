resource "aws_s3_bucket" "ai_data" {
  bucket = "${var.project_name}-ai-data"

  tags = var.common_tags
}

resource "aws_s3_bucket_public_access_block" "ai_data" {
  bucket = aws_s3_bucket.ai_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "ai_data" {
  bucket = aws_s3_bucket.ai_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ai_data" {
  bucket = aws_s3_bucket.ai_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}