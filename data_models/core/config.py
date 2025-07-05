# data_models/config.py

import os

# --- GCP Configuration ---
PROJECT_ID = "citypulse-21"
GCP_REGION = "us-central1"

# --- BigQuery Configuration ---
BIGQUERY_DATASET = "citypulse_analytics"
BIGQUERY_TABLE = "events"
BIGQUERY_TABLE_CITIZEN_REPORTS = "citizen_reports"
BIGQUERY_TABLE_IOT = "iot_data"
BIGQUERY_TABLE_OFFICIAL_FEEDS = "official_feeds"
BIGQUERY_TABLE_SOCIAL_MEDIA = "social_media_posts"

# --- Pub/Sub Topics ---
# These names should match the topics created in your Terraform setup
PUBSUB_CITIZEN_REPORTS_TOPIC = "citypulse-citizen_reports-ingestion"
PUBSUB_TWITTER_TOPIC = "citypulse-twitter-ingestion"
PUBSUB_IOT_SENSORS_TOPIC = "citypulse-iot_sensors-ingestion"
PUBSUB_OFFICIAL_FEEDS_TOPIC = "citypulse-official_feeds-ingestion"
PUBSUB_SOCIAL_MEDIA_TOPIC = "citypulse-social_media-ingestion"

# --- Cloud Storage ---
MULTIMEDIA_BUCKET_NAME = f"{PROJECT_ID}-multimedia"
GCS_GENERATED_IMAGES_BUCKET = f"{PROJECT_ID}-generated-images"

# --- Firestore Configuration ---
FIRESTORE_EVENTS_COLLECTION = "events"

# --- Service Account (Optional) ---
# If you need to specify a service account key file, you can set its path here.
# GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "path/to/your/keyfile.json")
