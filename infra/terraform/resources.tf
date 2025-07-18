# Use existing project
data "google_project" "project" {
  project_id = var.project_id
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "pubsub.googleapis.com",
    "dataflow.googleapis.com",
    "bigquery.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
    "cloudkms.googleapis.com",
    "compute.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])

  service = each.key
  project = data.google_project.project.project_id

  # Don't disable the service if the resource block is removed
  disable_on_destroy = false
}

# Create Pub/Sub topics for production
resource "google_pubsub_topic" "topics" {
  for_each = toset([
    "twitter",
    "citizen_reports",
    "iot_sensors",
    "official_feeds"
  ])

  name    = "citypulse-${each.key}-ingestion"
  project = data.google_project.project.project_id

  depends_on = [google_project_service.services["pubsub.googleapis.com"]]
}
#
# # Create BigQuery dataset for production
resource "google_bigquery_dataset" "analytics" {
  dataset_id    = "citypulse_analytics"
  friendly_name = "CityPulse Analytics Dataset"
  description   = "Dataset containing all analytics data for CityPulse"
  location      = var.region
  project       = data.google_project.project.project_id

  depends_on = [google_project_service.services["bigquery.googleapis.com"]]
}

# Create Cloud Storage bucket for Terraform state
resource "google_storage_bucket" "tf_state" {
  name          = "citypulse-tf-state"
  location      = var.region
  project       = data.google_project.project.project_id
  force_destroy = false

  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }

  depends_on = [google_project_service.services["storage.googleapis.com"]]
}

# Create Cloud Storage bucket
# resource "google_storage_bucket" "multimedia" {
#   name          = "${var.project_id}-multimedia"
#   location      = var.region
#   project       = data.google_project.project.project_id
#   force_destroy = false
#
#   uniform_bucket_level_access = true
#
#   depends_on = [google_project_service.services["storage.googleapis.com"]]
# }
#
# # Create Firestore database
# resource "google_firestore_database" "database" {
#   project     = data.google_project.project.project_id
#   name        = "(default)"
#   location_id = var.region
#   type        = "FIRESTORE_NATIVE"
#
#   depends_on = [google_project_service.services["firestore.googleapis.com"]]
# }

# Create Vertex AI resources
# resource "google_vertex_ai_featurestore" "featurestore" {
#   provider = google-beta
#   name     = "citypulse_featurestore"
#   region   = var.region
#   project  = data.google_project.project.project_id
#
#   online_serving_config {
#     fixed_node_count = 1
#   }
#
#   depends_on = [google_project_service.services["aiplatform.googleapis.com"]]
# }
#
# # Create service account for production applications
resource "google_service_account" "citypulse_sa" {
  account_id   = "citypulse-sa"
  display_name = "CityPulse Service Account"
  project      = data.google_project.project.project_id
}

# Assign IAM roles to the service account
# resource "google_project_iam_custom_role" "data_ingestion_role" {
#   role_id     = "dataIngestionRole"
#   project     = data.google_project.project.project_id
#   title       = "Data Ingestion Role"
#   description = "Permissions for data ingestion pipelines to write to Pub/Sub, BigQuery, and Firestore."
#   permissions = [
#     "pubsub.topics.publish",
#     "bigquery.tables.updateData",
#     "bigquery.jobs.create",
#     "datastore.entities.create",
#     "datastore.entities.update",
#   ]
# }
#
# resource "google_project_iam_member" "sa_data_ingestion_role" {
#   project = data.google_project.project.project_id
#   role    = google_project_iam_custom_role.data_ingestion_role.id
#   member  = "serviceAccount:${google_service_account.citypulse_sa.email}"
# }
#
# resource "google_project_iam_member" "sa_roles" {
#   for_each = toset([
#     "roles/dataflow.worker",
#     "roles/storage.objectAdmin",
#     "roles/aiplatform.user"
#   ])
#
#   project = data.google_project.project.project_id
#   role    = each.key
#   member  = "serviceAccount:${google_service_account.citypulse_sa.email}"
#
#   depends_on = [google_project_service.services["iam.googleapis.com"]]
# }

# Output important information
output "project_id" {
  value = data.google_project.project.project_id
}

# output "service_account_email" {
#   value = google_service_account.citypulse_sa.email
# }
#
# output "pubsub_topics" {
#   description = "The names of the created Pub/Sub topics."
#   value = {
#     for key, topic in google_pubsub_topic.topics : key => topic.name
#   }
# }
#
# output "bigquery_dataset" {
#   value = google_bigquery_dataset.analytics.dataset_id
# }
#
# output "storage_bucket" {
#   value = google_storage_bucket.multimedia.name
# }
