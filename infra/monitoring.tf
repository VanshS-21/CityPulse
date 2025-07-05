resource "google_monitoring_alert_policy" "pubsub_alert" {
  display_name = "Pub/Sub Message Count Alert"
  combiner     = "OR"
  conditions {
    display_name = "Pub/Sub message count"
    condition_threshold {
      filter          = "resource.type = \"pubsub_topic\" AND resource.labels.topic_id = \"citypulse-data-ingestion\" AND metric.type = \"pubsub.googleapis.com/topic/send_message_operation_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1000
      trigger {
        count = 1
      }
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.name]
}

resource "google_monitoring_alert_policy" "bigquery_alert" {
  display_name = "BigQuery Query Execution Time Alert"
  combiner     = "OR"
  conditions {
    display_name = "BigQuery query execution time"
    condition_threshold {
      filter          = "resource.type = \"bigquery_project\" AND metric.type = \"bigquery.googleapis.com/query/execution_times\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.alert_thresholds.bigquery_query_time
      trigger {
        count = 1
      }
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.name]
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "CityPulse Alerts"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
  force_delete = false
}

# Cloud Storage monitoring
resource "google_monitoring_alert_policy" "storage_alert" {
  display_name = "Cloud Storage Object Count Alert"
  combiner     = "OR"
  conditions {
    display_name = "Cloud Storage object count"
    condition_threshold {
      filter          = join("", [
        "resource.type = \"gcs_bucket\" ",
        "AND resource.labels.bucket_name = \"${google_storage_bucket.multimedia.name}\" ",
        "AND metric.type = \"storage.googleapis.com/storage/total_bytes\""
      ])
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.alert_thresholds.storage_usage_bytes
      trigger {
        count = 1
      }
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.name]
}

# Enable Cloud Monitoring API
resource "google_project_service" "monitoring" {
  service = "monitoring.googleapis.com"
  disable_on_destroy = false
}

# Create a dashboard
resource "google_monitoring_dashboard" "citypulse_dashboard" {
  dashboard_json = jsonencode({
    displayName = "CityPulse Dashboard"
    gridLayout = {
      columns = "2"
      widgets = [
        {
          title = "Pub/Sub Message Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"pubsub_topic\" resource.labels.topic_id=\"citypulse-data-ingestion\" metric.type=\"pubsub.googleapis.com/topic/send_message_operation_count\""
                  aggregation = {
                    alignmentPeriod   = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                  }
                }
                unitOverride = "1"
              }
              plotType   = "LINE"
              targetAxis = "Y1"
            }]
            yAxis = {
              label = "y1Axis"
              scale = "LINEAR"
            }
          }
        },
        {
          title = "BigQuery Query Execution Time"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"bigquery_project\" metric.type=\"bigquery.googleapis.com/query/execution_times\""
                  aggregation = {
                    alignmentPeriod   = "60s"
                    perSeriesAligner = "ALIGN_PERCENTILE_99"
                  }
                }
                unitOverride = "ms"
              }
              plotType   = "LINE"
              targetAxis = "Y1"
            }]
            yAxis = {
              label = "y1Axis"
              scale = "LINEAR"
            }
          }
        },
        {
          title = "Cloud Storage Usage"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"gcs_bucket\" resource.labels.bucket_name=\"citypulse-21-multimedia\" metric.type=\"storage.googleapis.com/storage/total_bytes\""
                  aggregation = {
                    alignmentPeriod   = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
                unitOverride = "By"
              }
              plotType   = "STACKED_BAR"
              targetAxis = "Y1"
            }]
            yAxis = {
              label = "y1Axis"
              scale = "LINEAR"
            }
          }
        }
      ]
    }
  })
}

# Add IAM permissions for monitoring
resource "google_project_iam_member" "monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.citypulse_sa.email}"
}

resource "google_project_iam_member" "monitoring_editor" {
  project = var.project_id
  role    = "roles/monitoring.editor"
  member  = "serviceAccount:${google_service_account.citypulse_sa.email}"
}
