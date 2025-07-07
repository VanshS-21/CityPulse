# Enhanced BigQuery Configuration with Performance Optimizations
# Implements 2024-2025 BigQuery best practices for CityPulse

# Main analytics dataset with optimized configuration
resource "google_bigquery_dataset" "citypulse_analytics_optimized" {
  dataset_id                  = "citypulse_analytics_optimized"
  friendly_name              = "CityPulse Analytics - Performance Optimized"
  description                 = "Optimized dataset for CityPulse analytics with partitioning and clustering"
  location                    = var.region
  project                     = var.project_id
  default_table_expiration_ms = 7776000000 # 90 days

  # Enhanced access control
  access {
    role          = "OWNER"
    user_by_email = var.admin_email
  }

  access {
    role          = "WRITER"
    user_by_email = google_service_account.dataflow_worker.email
  }

  access {
    role          = "READER"
    user_by_email = google_service_account.api_service.email
  }

  # Labels for cost tracking and organization
  labels = {
    environment = var.environment
    project     = "citypulse"
    cost_center = "analytics"
    team        = "data-engineering"
  }
}

# Optimized events table with partitioning and clustering
resource "google_bigquery_table" "events_optimized" {
  dataset_id = google_bigquery_dataset.citypulse_analytics_optimized.dataset_id
  table_id   = "events_optimized"
  project    = var.project_id

  description = "Optimized events table with time partitioning and location clustering"

  # Time partitioning for performance and cost optimization
  time_partitioning {
    type                     = "DAY"
    field                    = "created_at"
    require_partition_filter = true
    expiration_ms           = 7776000000 # 90 days
  }

  # Clustering for improved query performance
  clustering = ["location_hash", "category", "priority"]

  schema = jsonencode([
    {
      name = "id"
      type = "STRING"
      mode = "REQUIRED"
      description = "Unique event identifier"
    },
    {
      name = "event_id"
      type = "INT64"
      mode = "REQUIRED"
      description = "Numeric event ID for optimized joins"
    },
    {
      name = "title"
      type = "STRING"
      mode = "REQUIRED"
      description = "Event title"
    },
    {
      name = "description"
      type = "STRING"
      mode = "NULLABLE"
      description = "Event description"
    },
    {
      name = "category"
      type = "STRING"
      mode = "REQUIRED"
      description = "Event category (clustered field)"
    },
    {
      name = "priority"
      type = "STRING"
      mode = "REQUIRED"
      description = "Event priority level (clustered field)"
    },
    {
      name = "status"
      type = "STRING"
      mode = "REQUIRED"
      description = "Current event status"
    },
    {
      name = "location"
      type = "RECORD"
      mode = "REQUIRED"
      description = "Event location information"
      fields = [
        {
          name = "latitude"
          type = "FLOAT64"
          mode = "REQUIRED"
        },
        {
          name = "longitude"
          type = "FLOAT64"
          mode = "REQUIRED"
        },
        {
          name = "address"
          type = "STRING"
          mode = "NULLABLE"
        },
        {
          name = "district"
          type = "STRING"
          mode = "NULLABLE"
        }
      ]
    },
    {
      name = "location_hash"
      type = "STRING"
      mode = "REQUIRED"
      description = "Geohash for location clustering (clustered field)"
    },
    {
      name = "reporter_info"
      type = "RECORD"
      mode = "NULLABLE"
      description = "Information about the event reporter"
      fields = [
        {
          name = "user_id"
          type = "STRING"
          mode = "NULLABLE"
        },
        {
          name = "user_type"
          type = "STRING"
          mode = "NULLABLE"
        },
        {
          name = "contact_method"
          type = "STRING"
          mode = "NULLABLE"
        }
      ]
    },
    {
      name = "ai_analysis"
      type = "RECORD"
      mode = "NULLABLE"
      description = "AI-generated analysis and insights"
      fields = [
        {
          name = "sentiment_score"
          type = "FLOAT64"
          mode = "NULLABLE"
        },
        {
          name = "urgency_score"
          type = "FLOAT64"
          mode = "NULLABLE"
        },
        {
          name = "tags"
          type = "STRING"
          mode = "REPEATED"
        },
        {
          name = "summary"
          type = "STRING"
          mode = "NULLABLE"
        }
      ]
    },
    {
      name = "media_files"
      type = "RECORD"
      mode = "REPEATED"
      description = "Associated media files"
      fields = [
        {
          name = "file_url"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "file_type"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "file_size"
          type = "INT64"
          mode = "NULLABLE"
        }
      ]
    },
    {
      name = "created_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
      description = "Event creation timestamp (partitioning field)"
    },
    {
      name = "updated_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
      description = "Last update timestamp"
    },
    {
      name = "metadata"
      type = "JSON"
      mode = "NULLABLE"
      description = "Additional metadata in JSON format"
    }
  ])

  # Deletion protection
  deletion_protection = true

  labels = {
    environment = var.environment
    table_type  = "events"
    optimized   = "true"
  }
}

# Materialized view for frequently accessed aggregations
resource "google_bigquery_table" "events_daily_summary" {
  dataset_id = google_bigquery_dataset.citypulse_analytics_optimized.dataset_id
  table_id   = "events_daily_summary_mv"
  project    = var.project_id

  description = "Materialized view for daily event summaries"

  materialized_view {
    query = <<-SQL
      SELECT
        DATE(created_at) as event_date,
        category,
        priority,
        status,
        location.district,
        COUNT(*) as event_count,
        COUNTIF(priority = 'critical') as critical_events,
        COUNTIF(priority = 'high') as high_priority_events,
        AVG(ai_analysis.urgency_score) as avg_urgency_score,
        AVG(ai_analysis.sentiment_score) as avg_sentiment_score,
        ARRAY_AGG(DISTINCT ai_analysis.tags IGNORE NULLS) as all_tags
      FROM `${var.project_id}.${google_bigquery_dataset.citypulse_analytics_optimized.dataset_id}.events_optimized`
      WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
      GROUP BY 1, 2, 3, 4, 5
    SQL

    enable_refresh = true
    refresh_interval_ms = 3600000 # Refresh every hour
  }

  labels = {
    environment = var.environment
    table_type  = "materialized_view"
    purpose     = "daily_summary"
  }
}

# Search index for text-based queries
resource "google_bigquery_table" "events_search_index" {
  dataset_id = google_bigquery_dataset.citypulse_analytics_optimized.dataset_id
  table_id   = "events_search_index"
  project    = var.project_id

  description = "Search index table for optimized text searches"

  schema = jsonencode([
    {
      name = "event_id"
      type = "INT64"
      mode = "REQUIRED"
    },
    {
      name = "search_text"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "search_vector"
      type = "STRING"
      mode = "NULLABLE"
      description = "Text search vector for full-text search"
    },
    {
      name = "indexed_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])

  # Clustering on search-related fields
  clustering = ["search_text"]

  labels = {
    environment = var.environment
    table_type  = "search_index"
  }
}

# Performance monitoring table
resource "google_bigquery_table" "query_performance_metrics" {
  dataset_id = google_bigquery_dataset.citypulse_analytics_optimized.dataset_id
  table_id   = "query_performance_metrics"
  project    = var.project_id

  description = "Table for tracking query performance metrics"

  time_partitioning {
    type  = "DAY"
    field = "query_timestamp"
  }

  schema = jsonencode([
    {
      name = "query_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "query_text"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "query_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "execution_time_ms"
      type = "INT64"
      mode = "REQUIRED"
    },
    {
      name = "bytes_processed"
      type = "INT64"
      mode = "REQUIRED"
    },
    {
      name = "bytes_shuffled"
      type = "INT64"
      mode = "NULLABLE"
    },
    {
      name = "slot_time_ms"
      type = "INT64"
      mode = "NULLABLE"
    },
    {
      name = "user_email"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "optimization_suggestions"
      type = "STRING"
      mode = "REPEATED"
    }
  ])

  labels = {
    environment = var.environment
    table_type  = "performance_metrics"
  }
}

# Cost optimization scheduled query
resource "google_bigquery_data_transfer_config" "cost_optimization_analysis" {
  display_name   = "CityPulse Cost Optimization Analysis"
  location       = var.region
  data_source_id = "scheduled_query"
  schedule       = "every day 06:00"
  project        = var.project_id

  destination_dataset_id = google_bigquery_dataset.citypulse_analytics_optimized.dataset_id

  params = {
    destination_table_name_template = "cost_analysis_{run_date}"
    write_disposition               = "WRITE_TRUNCATE"
    query = <<-SQL
      WITH query_costs AS (
        SELECT
          DATE(query_timestamp) as query_date,
          user_email,
          COUNT(*) as query_count,
          SUM(bytes_processed) as total_bytes_processed,
          AVG(execution_time_ms) as avg_execution_time,
          SUM(bytes_processed) * 5.0 / POW(10, 12) as estimated_cost_usd
        FROM `${var.project_id}.${google_bigquery_dataset.citypulse_analytics_optimized.dataset_id}.query_performance_metrics`
        WHERE query_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY 1, 2
      ),
      optimization_opportunities AS (
        SELECT
          query_date,
          user_email,
          query_count,
          total_bytes_processed,
          avg_execution_time,
          estimated_cost_usd,
          CASE 
            WHEN avg_execution_time > 10000 THEN 'Consider query optimization'
            WHEN total_bytes_processed > POW(10, 11) THEN 'High data processing - check for SELECT *'
            WHEN query_count > 100 THEN 'High query frequency - consider caching'
            ELSE 'No immediate optimization needed'
          END as optimization_recommendation
        FROM query_costs
      )
      SELECT * FROM optimization_opportunities
      ORDER BY estimated_cost_usd DESC
    SQL
  }

  depends_on = [google_bigquery_table.query_performance_metrics]
}

# Output optimized dataset information
output "optimized_dataset_id" {
  description = "ID of the optimized BigQuery dataset"
  value       = google_bigquery_dataset.citypulse_analytics_optimized.dataset_id
}

output "optimized_events_table" {
  description = "Full name of the optimized events table"
  value       = "${var.project_id}.${google_bigquery_dataset.citypulse_analytics_optimized.dataset_id}.${google_bigquery_table.events_optimized.table_id}"
}

output "materialized_view_name" {
  description = "Name of the daily summary materialized view"
  value       = google_bigquery_table.events_daily_summary.table_id
}
