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
    random = {
      source  = "hashicorp/random"
      version = "3.1.0"
    }
  }
  required_version = ">= 1.0.0"
}

resource "random_pet" "suffix" {
  length = 2
}

resource "google_storage_bucket" "temp" {
  name          = "${var.project_id}-temp-${random_pet.suffix.id}"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "staging" {
  name          = "${var.project_id}-staging-${random_pet.suffix.id}"
  location      = var.region
  force_destroy = true
}

# Configure the Google Cloud providers
provider "google" {
  credentials = file("../keys/citypulse-21-90f84cb134a2.json")
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

output "gcs_temp_bucket" {
  value = google_storage_bucket.temp.url
}

output "gcs_staging_bucket" {
  value = google_storage_bucket.staging.url
}

provider "google-beta" {
  credentials = file("../keys/citypulse-21-90f84cb134a2.json")
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}
