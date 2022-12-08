locals {
  # default for cases when `null` value provided, meaning "use default"
  search_regions    = var.search_regions == null ? [] : var.search_regions
  search_accounts   = var.search_accounts == null ? [] : var.search_accounts
  peering_role_name = var.peering_role_name == null ? "" : var.peering_role_name
}
