data "aws_iam_policy_document" "auto_peering_assume_role_policy" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type = "Service"
    }
  }
}

resource "aws_iam_role" "auto_peering" {
  name = "auto-peering-role-${var.region}-${var.deployment_identifier}"
  assume_role_policy = data.aws_iam_policy_document.auto_peering_assume_role_policy.json
}

data "aws_iam_policy_document" "auto_peering_role_policy" {
  statement {
    effect = "Allow"
    resources = ["*"]

    actions = [
      "ec2:AcceptVpcPeeringConnection",
      "ec2:CreateVpcPeeringConnection",
      "ec2:DeleteVpcPeeringConnection",
      "ec2:DescribeVpcPeeringConnections",
      "ec2:CreateRoute",
      "ec2:DeleteRoute",
      "ec2:DescribeRouteTables",
      "ec2:DescribeTags",
      "ec2:DescribeVpcs",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
  }
}

resource "aws_iam_policy" "auto_peering" {
  name = "auto-peering-policy-${var.region}-${var.deployment_identifier}"
  description = "auto-peering-policy-${var.region}-${var.deployment_identifier}"
  policy = data.aws_iam_policy_document.auto_peering_role_policy.json
}

resource "aws_iam_policy_attachment" "auto_peering" {
  name = "auto-peering-policy-attachment-${var.region}-${var.deployment_identifier}"
  roles = [aws_iam_role.auto_peering.id]
  policy_arn = aws_iam_policy.auto_peering.arn
}
