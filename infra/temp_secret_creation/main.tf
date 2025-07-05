terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.85.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "us-central1-c"
}

resource "google_secret_manager_secret" "service_account_key" {
  secret_id = "service-account-key"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "service_account_key_version" {
  secret      = google_secret_manager_secret.service_account_key.id
  secret_data = file("../keys/service-acc-key.json")
}
