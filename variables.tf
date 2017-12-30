variable "region" {
  description = "The region into which the VPC auto peering lambda is being deployed."
}
variable "deployment_identifier" {
  description = "An identifier for this instantiation."
}

variable "infrastructure_events_topic_arn" {
  description = "The ARN of the SNS topic containing VPC events."
}
