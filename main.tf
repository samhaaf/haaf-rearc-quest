provider "aws" {
  shared_credentials_files = ["~/.aws/credentials"]
  region = "us-east-1"
}


resource "aws_iam_role" "haaf_rearc_quest_role" {
  name = "haaf_rearc_quest_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  inline_policy {
    name = "my_inline_policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = "*"
        },{
          Action = [
            "s3:*"
          ]
          Effect = "Allow"
          Resource = "arn:aws:s3:::haaf-rearc-quest/*"
        },{
          Action = "sqs:*"
          Effect = "Allow"
          Resource = "arn:aws:sqs:*:*:haaf_rearc_quest_queue"
        }
      ]
    })
  }
}


resource "aws_lambda_function" "haaf_rearc_quest_scrape_fn" {
  filename      = "scrape_lambda/_lambda_payload.zip"
  function_name = "haaf_rearc_quest_scrape_fn"
  role          = aws_iam_role.haaf_rearc_quest_role.arn
  handler       = "lambda_handler.lambda_handler"

  source_code_hash = filebase64sha256("scrape_lambda/_lambda_payload.zip")

  runtime = "python3.9"
  timeout = 60

  environment {
    variables = {
      for tuple in regexall("(\\w*)=(.*)", file("scrape_lambda/env.env")) : tuple[0] => tuple[1]
    }
  }
}


resource "aws_cloudwatch_event_rule" "haaf_rearc_quest_schedule" {
    name = "haaf_rearc_quest_schedule"
    description = "Schedule for Lambda Function"
    schedule_expression = "cron(0 0 * * ? *)"
}


resource "aws_cloudwatch_event_target" "haaf_rearc_quest_lambda_target" {
    rule = aws_cloudwatch_event_rule.haaf_rearc_quest_schedule.name
    target_id = "haaf_rearc_quest_fn"
    arn = aws_lambda_function.haaf_rearc_quest_scrape_fn.arn
}


resource "aws_lambda_permission" "allow_events_bridge_to_run_lambda" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.haaf_rearc_quest_scrape_fn.function_name
    principal = "events.amazonaws.com"
}


resource "aws_sqs_queue" "haaf_rearc_quest_queue" {
  name                      = "haaf_rearc_quest_queue"
  visibility_timeout_seconds= 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  
}


resource "aws_s3_object" "lambda_zip" {
  bucket = trim(ws_lambda_function.haaf_rearc_quest_scrape_fn.environment[0].variables.S3_BUCKET, "\"")
  key    = "lambda-functions/haaf_rearc_quest_report_fn.zip"
  source = "report_lambda/_lambda_payload.zip"
}


resource "aws_lambda_function" "haaf_rearc_quest_report_fn" {
  s3_bucket   = aws_s3_object.lambda_zip.bucket
  s3_key      = aws_s3_object.lambda_zip.key

  function_name = "haaf_rearc_quest_report_fn"
  role          = aws_iam_role.haaf_rearc_quest_role.arn
  handler       = "lambda_handler.lambda_handler"

  source_code_hash = filebase64sha256("report_lambda/_lambda_payload.zip")

  runtime = "python3.9"
  timeout = 60

  environment {
    variables = {
      for tuple in regexall("(\\w*)=(.*)", file("report_lambda/env.env")) : tuple[0] => tuple[1]
    }
  }
}


resource "aws_lambda_event_source_mapping" "haaf_rearc_quest_event_source_mapping" {
  event_source_arn = aws_sqs_queue.haaf_rearc_quest_queue.arn
  enabled          = true
  function_name    = aws_lambda_function.haaf_rearc_quest_report_fn.arn
  batch_size       = 1
}
