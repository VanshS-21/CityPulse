# Enhanced Security Configuration for CityPulse
# Implements 2024-2025 GCP security best practices

# Dedicated service accounts with minimal permissions
resource "google_service_account" "dataflow_worker" {
  account_id   = "citypulse-dataflow-worker"
  display_name = "CityPulse Dataflow Worker Service Account"
  description  = "Dedicated service account for Dataflow workers with minimal permissions"
  project      = var.project_id
}

resource "google_service_account" "ai_processor" {
  account_id   = "citypulse-ai-processor"
  display_name = "CityPulse AI Processing Service Account"
  description  = "Service account for AI/ML processing tasks"
  project      = var.project_id
}

resource "google_service_account" "api_service" {
  account_id   = "citypulse-api-service"
  display_name = "CityPulse API Service Account"
  description  = "Service account for API services and Cloud Run"
  project      = var.project_id
}

# Custom IAM roles with principle of least privilege
resource "google_project_iam_custom_role" "citizen_report_processor" {
  role_id     = "citizenReportProcessor"
  title       = "Citizen Report Processor"
  description = "Custom role for processing citizen reports with minimal permissions"
  project     = var.project_id
  
  permissions = [
    "pubsub.messages.ack",
    "pubsub.subscriptions.consume",
    "bigquery.tables.updateData",
    "bigquery.tables.get",
    "storage.objects.create",
    "storage.objects.get",
    "firestore.documents.write",
    "firestore.documents.get",
    "logging.logEntries.create"
  ]
}

resource "google_project_iam_custom_role" "ai_data_processor" {
  role_id     = "aiDataProcessor"
  title       = "AI Data Processor"
  description = "Custom role for AI processing with Vertex AI access"
  project     = var.project_id
  
  permissions = [
    "aiplatform.endpoints.predict",
    "aiplatform.models.predict",
    "storage.objects.get",
    "storage.objects.create",
    "bigquery.tables.updateData",
    "bigquery.tables.get",
    "firestore.documents.write",
    "firestore.documents.get"
  ]
}

resource "google_project_iam_custom_role" "api_service_role" {
  role_id     = "apiServiceRole"
  title       = "API Service Role"
  description = "Custom role for API services"
  project     = var.project_id
  
  permissions = [
    "firestore.documents.read",
    "firestore.documents.write",
    "bigquery.jobs.create",
    "bigquery.tables.getData",
    "storage.objects.get",
    "pubsub.topics.publish",
    "logging.logEntries.create"
  ]
}

# Bind custom roles to service accounts
resource "google_project_iam_member" "dataflow_worker_binding" {
  project = var.project_id
  role    = google_project_iam_custom_role.citizen_report_processor.name
  member  = "serviceAccount:${google_service_account.dataflow_worker.email}"
}

resource "google_project_iam_member" "ai_processor_binding" {
  project = var.project_id
  role    = google_project_iam_custom_role.ai_data_processor.name
  member  = "serviceAccount:${google_service_account.ai_processor.email}"
}

resource "google_project_iam_member" "api_service_binding" {
  project = var.project_id
  role    = google_project_iam_custom_role.api_service_role.name
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

# Additional required roles for Dataflow
resource "google_project_iam_member" "dataflow_worker_role" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_worker.email}"
}

# Private VPC for secure networking
resource "google_compute_network" "citypulse_vpc" {
  name                    = "citypulse-private-network"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "dataflow_subnet" {
  name          = "citypulse-dataflow-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.citypulse_vpc.id
  project       = var.project_id
  
  # Enable private Google access for secure API communication
  private_ip_google_access = true
  
  # Secondary ranges for additional services if needed
  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "10.1.0.0/16"
  }
}

resource "google_compute_subnetwork" "api_subnet" {
  name          = "citypulse-api-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.citypulse_vpc.id
  project       = var.project_id
  
  private_ip_google_access = true
}

# Firewall rules for secure communication
resource "google_compute_firewall" "dataflow_internal" {
  name    = "citypulse-dataflow-internal"
  network = google_compute_network.citypulse_vpc.name
  project = var.project_id
  
  allow {
    protocol = "tcp"
    ports    = ["12345-12346"] # Dataflow worker communication
  }
  
  source_ranges = ["10.0.1.0/24"]
  target_tags   = ["dataflow-worker"]
  
  description = "Allow internal communication between Dataflow workers"
}

resource "google_compute_firewall" "api_internal" {
  name    = "citypulse-api-internal"
  network = google_compute_network.citypulse_vpc.name
  project = var.project_id
  
  allow {
    protocol = "tcp"
    ports    = ["8080", "443"]
  }
  
  source_ranges = ["10.0.2.0/24"]
  target_tags   = ["api-service"]
  
  description = "Allow internal API communication"
}

resource "google_compute_firewall" "deny_all_ingress" {
  name      = "citypulse-deny-all-ingress"
  network   = google_compute_network.citypulse_vpc.name
  project   = var.project_id
  direction = "INGRESS"
  priority  = 65534
  
  deny {
    protocol = "all"
  }
  
  source_ranges = ["0.0.0.0/0"]
  
  description = "Deny all ingress traffic by default"
}

# Cloud NAT for outbound internet access from private instances
resource "google_compute_router" "citypulse_router" {
  name    = "citypulse-router"
  region  = var.region
  network = google_compute_network.citypulse_vpc.id
  project = var.project_id
}

resource "google_compute_router_nat" "citypulse_nat" {
  name                               = "citypulse-nat"
  router                             = google_compute_router.citypulse_router.name
  region                             = var.region
  project                            = var.project_id
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Customer-managed encryption keys for enhanced security
resource "google_kms_key_ring" "citypulse_keyring" {
  name     = "citypulse-keyring"
  location = var.region
  project  = var.project_id
}

resource "google_kms_crypto_key" "dataflow_key" {
  name     = "citypulse-dataflow-key"
  key_ring = google_kms_key_ring.citypulse_keyring.id
  
  lifecycle {
    prevent_destroy = true
  }
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
}

resource "google_kms_crypto_key" "storage_key" {
  name     = "citypulse-storage-key"
  key_ring = google_kms_key_ring.citypulse_keyring.id
  
  lifecycle {
    prevent_destroy = true
  }
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
}

# IAM bindings for KMS keys
resource "google_kms_crypto_key_iam_member" "dataflow_key_user" {
  crypto_key_id = google_kms_crypto_key.dataflow_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_service_account.dataflow_worker.email}"
}

resource "google_kms_crypto_key_iam_member" "storage_key_user" {
  crypto_key_id = google_kms_crypto_key.storage_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_service_account.api_service.email}"
}

# Security policies and organization constraints
resource "google_project_organization_policy" "disable_service_account_key_creation" {
  project    = var.project_id
  constraint = "iam.disableServiceAccountKeyCreation"
  
  boolean_policy {
    enforced = true
  }
}

resource "google_project_organization_policy" "require_os_login" {
  project    = var.project_id
  constraint = "compute.requireOsLogin"
  
  boolean_policy {
    enforced = true
  }
}

# Audit logging configuration
resource "google_logging_project_sink" "security_sink" {
  name        = "citypulse-security-audit-sink"
  project     = var.project_id
  destination = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"
  
  filter = <<EOF
protoPayload.serviceName="iam.googleapis.com" OR
protoPayload.serviceName="cloudkms.googleapis.com" OR
protoPayload.serviceName="compute.googleapis.com" OR
severity>=ERROR
EOF
  
  unique_writer_identity = true
}

resource "google_storage_bucket" "audit_logs" {
  name     = "${var.project_id}-security-audit-logs"
  location = var.region
  project  = var.project_id
  
  # Enable versioning for audit trail
  versioning {
    enabled = true
  }
  
  # Lifecycle management for cost optimization
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }
  
  # Encryption with customer-managed key
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }
  
  # Prevent public access
  public_access_prevention = "enforced"
}

# Grant the logging sink permission to write to the bucket
resource "google_storage_bucket_iam_member" "audit_logs_writer" {
  bucket = google_storage_bucket.audit_logs.name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.security_sink.writer_identity
}

# Output important security information
output "dataflow_worker_service_account" {
  description = "Email of the Dataflow worker service account"
  value       = google_service_account.dataflow_worker.email
}

output "ai_processor_service_account" {
  description = "Email of the AI processor service account"
  value       = google_service_account.ai_processor.email
}

output "api_service_account" {
  description = "Email of the API service account"
  value       = google_service_account.api_service.email
}

output "vpc_network_name" {
  description = "Name of the private VPC network"
  value       = google_compute_network.citypulse_vpc.name
}

output "dataflow_subnet_name" {
  description = "Name of the Dataflow subnet"
  value       = google_compute_subnetwork.dataflow_subnet.name
}

output "kms_keyring_id" {
  description = "ID of the KMS key ring"
  value       = google_kms_key_ring.citypulse_keyring.id
}
