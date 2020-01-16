locals {
  assumable_roles = [
    for account in var.search_accounts:
          "arn:aws:iam::${account}:role/${var.peering_role_name}"
  ]
}

data "aws_iam_policy_document" "vpc_auto_peering_lambda_assume_role_policy" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type = "Service"
    }
  }
}

data "aws_iam_policy_document" "vpc_auto_peering_lambda_policy" {
  statement {
    effect = "Allow"
    resources = local.assumable_roles

    actions = [
      "sts:AssumeRole"
    ]
  }
  statement {
    effect = "Allow"
    resources = ["*"]

    actions = [
      "sts:GetCallerIdentity",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
  }
}

resource "aws_iam_role" "vpc_auto_peering_lambda" {
  name = "vpc-auto-peering-lambda-role-${var.region}-${var.deployment_identifier}"
  assume_role_policy = data.aws_iam_policy_document.vpc_auto_peering_lambda_assume_role_policy.json
}

resource "aws_iam_policy" "vpc_auto_peering_lambda" {
  name = "vpc-auto-peering-lambda-policy-${var.region}-${var.deployment_identifier}"
  description = "vpc-auto-peering-lambda-policy"
  policy = data.aws_iam_policy_document.vpc_auto_peering_lambda_policy.json
}

resource "aws_iam_policy_attachment" "vpc_auto_peering_lambda" {
  name = "vpc-auto-peering-lambda-policy-attachment-${var.region}-${var.deployment_identifier}"
  roles = [aws_iam_role.vpc_auto_peering_lambda.id]
  policy_arn = aws_iam_policy.vpc_auto_peering_lambda.arn
}
