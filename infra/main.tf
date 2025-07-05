terraform {

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.85.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "4.85.0"
    }
  }
  required_version = ">= 1.0.0"
}

# Configure the Google Cloud providers
provider "google" {
  credentials = file("../keys/service-acc-key.json")
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

provider "google-beta" {
  credentials = file("../keys/service-acc-key.json")
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}
