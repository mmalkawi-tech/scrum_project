terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "azurerm" {
    resource_group_name  = "medappoint-tfstate-rg"
    storage_account_name = "medappointtfstate123"
    container_name        = "tfstate"
    key                    = "medappoint.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}