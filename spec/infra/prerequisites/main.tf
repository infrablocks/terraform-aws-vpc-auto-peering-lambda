resource "aws_sns_topic" "infrastructure_events" {
  name = "infrastructure-events-topic-${var.region}-${var.deployment_identifier}"
}
