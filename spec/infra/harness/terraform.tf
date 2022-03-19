terraform {
  required_version = ">= 1.0"

  required_providers {
    aws     = {
      source  = "hashicorp/aws"
      version = "~> 3.33"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.1"
    }
  }
}
