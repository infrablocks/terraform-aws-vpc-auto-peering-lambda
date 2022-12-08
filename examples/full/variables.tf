variable "region" {}

variable "deployment_identifier" {}

variable "search_regions" {
  type = list(string)
}
variable "search_accounts" {
  type = list(string)
}
variable "peering_role_name" {}
