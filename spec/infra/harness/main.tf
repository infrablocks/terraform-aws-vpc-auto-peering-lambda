data "terraform_remote_state" "prerequisites" {
  backend = "local"

  config {
    path = "${path.module}/../../../../state/prerequisites.tfstate"
  }
}

module "vpc_auto_peering" {
  source = "../../../../"

  region = "${var.region}"
  deployment_identifier = "${var.deployment_identifier}"

  infrastructure_events_topic_arn = "${data.terraform_remote_state.prerequisites.infrastructure_events_topic_arn}"
}
