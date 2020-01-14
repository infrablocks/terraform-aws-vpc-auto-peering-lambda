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
variable "search_accounts" {
  description = "IDs of AWS accounts to search for dependency and dependent VPCs."
  type = list(string)
  default = []
}
variable "peering_role_name" {
  description = "The name of the role to assume to create peering relationships and routes."
  type = string
  default = ""
}
variable "assumable_roles" {
  type = list(string)
  default = []
  description = "A list of role ARNs corresponding to roles that should be assumable by the lambda."
}
