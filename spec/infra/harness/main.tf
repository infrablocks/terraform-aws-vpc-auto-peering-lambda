data "terraform_remote_state" "prerequisites" {
  backend = "local"

  config = {
    path = "${path.module}/../../../../state/prerequisites.tfstate"
  }
}

module "vpc_auto_peering_lambda" {
  source = "../../../../"

  region = var.region
  deployment_identifier = var.deployment_identifier

  infrastructure_events_topic_arn = data.terraform_remote_state.prerequisites.outputs.infrastructure_events_topic_arn

  search_regions = var.search_regions
  search_accounts = var.search_accounts
  peering_role_name = var.peering_role_name
  assumable_roles = var.assumable_roles
}
