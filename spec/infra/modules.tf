resource "aws_sns_topic" "infrastructure_events" {
  name = "infrastructure-events-topic-${var.region}-${var.deployment_identifier}"
}

module "vpc_auto_peering" {
  source = "../../src"

  region = "${var.region}"
  deployment_identifier = "${var.deployment_identifier}"

  infrastructure_events_topic_arn = "${aws_sns_topic.infrastructure_events.arn}"
}
