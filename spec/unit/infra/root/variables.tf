variable "region" {}
variable "deployment_identifier" {}

variable "search_regions" {
  type = list(string)
  default = null
}
variable "search_accounts" {
  type = list(string)
  default = null
}
variable "peering_role_name" {
  default = null
}
