data "archive_file" "auto_peering_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-definitions/auto_peering"
  output_path = "${path.cwd}/build/auto_peering.zip"
}

resource "aws_lambda_function" "auto_peering" {
  filename = "${path.cwd}/build/auto_peering.zip"
  function_name = "auto-peering-${var.region}-${var.deployment_identifier}"
  handler = "auto_peering_lambda.peer_vpcs_for"
  role = "${aws_iam_role.auto_peering.arn}"
  runtime = "python3.6"
  timeout = 300
  source_code_hash = "${base64sha256(file("${path.cwd}/build/auto_peering.zip"))}"

  depends_on = ["data.archive_file.auto_peering_lambda_zip"]
}
