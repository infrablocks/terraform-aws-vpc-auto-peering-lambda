module "vpc_auto_peering_lambda" {
  source = "./../../"

  region = var.region
  deployment_identifier = var.deployment_identifier

  infrastructure_events_topic_arn = aws_sns_topic.infrastructure_events.arn

  search_regions = var.search_regions
  search_accounts = var.search_accounts
  peering_role_name = var.peering_role_name
}
