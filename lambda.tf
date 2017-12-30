data "archive_file" "auto_peering_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/auto_peering"
  output_path = "${path.cwd}/build/auto_peering.zip"
}

resource "aws_lambda_function" "auto_peering" {
  filename = "${data.archive_file.auto_peering_lambda_zip.output_path}"
  function_name = "auto-peering-${var.region}-${var.deployment_identifier}"
  handler = "auto_peering_lambda.peer_vpcs_for"
  role = "${aws_iam_role.auto_peering.arn}"
  runtime = "python3.6"
  timeout = 300
  source_code_hash = "${data.archive_file.auto_peering_lambda_zip.output_base64sha256}"
}
