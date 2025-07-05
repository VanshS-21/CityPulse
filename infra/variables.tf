variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region where resources will be created"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone where resources will be created"
  type        = string
  default     = "us-central1-a"
}

variable "billing_account" {
  description = "The ID of the billing account to associate with the project"
  type        = string
  sensitive   = true
}

variable "org_id" {
  description = "The organization ID (optional for individual accounts)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "project_name" {
  description = "The name of the GCP project"
  type        = string
  default     = "citypulse"
}

variable "alert_email" {
  description = "Email address to receive monitoring alerts"
  type        = string
  default     = "superiorth16ismax@gmail.com"
}

variable "alert_thresholds" {
  description = "Thresholds for various monitoring alerts"
  type = object({
    pubsub_message_count = number
    bigquery_query_time  = number  # in milliseconds
    storage_usage_bytes  = number  # in bytes
  })
  default = {
    pubsub_message_count = 1000
    bigquery_query_time  = 10000    # 10 seconds
    storage_usage_bytes  = 1000000000  # 1GB
  }
}
