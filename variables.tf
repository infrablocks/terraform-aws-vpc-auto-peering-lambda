variable "region" {
  description = "The region into which the VPC auto peering lambda is being deployed."
  type = string
}
variable "deployment_identifier" {
  description = "An identifier for this instantiation."
  type = string
}

variable "infrastructure_events_topic_arn" {
  description = "The ARN of the SNS topic containing VPC events."
  type = string
}

variable "search_regions" {
  description = "AWS regions to search for dependency and dependent VPCs."
  type = list(string)
  default = []
}
