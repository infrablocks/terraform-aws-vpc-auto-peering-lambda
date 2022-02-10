terraform {
  required_version = ">= 0.14"

  required_providers {
    aws     = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.1"
    }
  }
}
