data "archive_file" "auto_peering_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/auto_peering"
  output_path = "${path.cwd}/build/auto_peering.zip"
}

resource "aws_lambda_function" "auto_peering" {
  filename = data.archive_file.auto_peering_lambda_zip.output_path
  function_name = "vpc-auto-peering-lambda-${var.region}-${var.deployment_identifier}"
  handler = "vpc_auto_peering_lambda.peer_vpcs_for"
  role = aws_iam_role.vpc_auto_peering_lambda.arn
  runtime = "python3.9"
  timeout = 300
  source_code_hash = data.archive_file.auto_peering_lambda_zip.output_base64sha256
  reserved_concurrent_executions = 1

  environment {
    variables = {
      AWS_SEARCH_REGIONS = join(",", local.search_regions)
      AWS_SEARCH_ACCOUNTS = join(",", local.search_accounts)
      AWS_PEERING_ROLE_NAME = local.peering_role_name
    }
  }
}
