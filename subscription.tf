resource "aws_lambda_permission" "infrastructure_events_topic_auto_peering_lambda" {
  statement_id = "AllowExecutionFromSNS"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.auto_peering.arn}"
  principal = "sns.amazonaws.com"
  source_arn = "${var.infrastructure_events_topic_arn}"
}

resource "aws_sns_topic_subscription" "infrastructure_events_topic_auto_peering_lambda" {
  topic_arn = "${var.infrastructure_events_topic_arn}"
  protocol = "lambda"
  endpoint = "${aws_lambda_function.auto_peering.arn}"
}
