output "infrastructure_events_topic_arn" {
  value = "${aws_sns_topic.infrastructure_events.arn}"
}