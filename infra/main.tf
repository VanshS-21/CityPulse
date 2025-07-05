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

data "google_secret_manager_secret_version" "service_account_key_data" {
  secret  = google_secret_manager_secret.service_account_key.id
  version = google_secret_manager_secret_version.service_account_key_version.version
}

# Configure the Google Cloud providers
provider "google" {
  credentials = data.google_secret_manager_secret_version.service_account_key_data.secret_data
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

provider "google-beta" {
  credentials = data.google_secret_manager_secret_version.service_account_key_data.secret_data
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}