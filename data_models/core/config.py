# data_models/config.py

import os

# --- GCP Configuration ---
# The unique identifier for your Google Cloud project.
PROJECT_ID = "citypulse-21"
# The default region for GCP resources.
GCP_REGION = "us-central1"

# --- BigQuery Configuration ---
# The name of the BigQuery dataset for storing analytical data.
BIGQUERY_DATASET = "citypulse_analytics"
# The main table for storing processed event data.
BIGQUERY_TABLE = "events"
# Table for storing raw data from citizen reports.
BIGQUERY_TABLE_CITIZEN_REPORTS = "citizen_reports"
# Table for storing data from IoT sensors.
BIGQUERY_TABLE_IOT = "iot_data"
# Table for storing data from official government feeds.
BIGQUERY_TABLE_OFFICIAL_FEEDS = "official_feeds"
# Table for storing data from social media sources.
BIGQUERY_TABLE_SOCIAL_MEDIA = "social_media_posts"

# --- Pub/Sub Topics ---
# These topic names must match the Pub/Sub topics created in your GCP project.
# Topic for ingesting citizen-reported events.
PUBSUB_CITIZEN_REPORTS_TOPIC = "citypulse-citizen_reports-ingestion"
# Topic for ingesting data from Twitter.
PUBSUB_TWITTER_TOPIC = "citypulse-twitter-ingestion"
# Topic for ingesting data from IoT sensors.
PUBSUB_IOT_SENSORS_TOPIC = "citypulse-iot_sensors-ingestion"
# Topic for ingesting data from official government feeds.
PUBSUB_OFFICIAL_FEEDS_TOPIC = "citypulse-official_feeds-ingestion"
# Topic for ingesting data from various social media platforms.
PUBSUB_SOCIAL_MEDIA_TOPIC = "citypulse-social_media-ingestion"

# --- Cloud Storage ---
# The GCS bucket for storing user-uploaded multimedia files.
MULTIMEDIA_BUCKET_NAME = f"{PROJECT_ID}-multimedia"
# The GCS bucket for storing AI-generated images.
GCS_GENERATED_IMAGES_BUCKET = f"{PROJECT_ID}-generated-images"

# --- Firestore Configuration ---
# The name of the Firestore collection for storing real-time event data.
FIRESTORE_EVENTS_COLLECTION = "events"

# --- Service Account (Optional) ---
# If you are running the application outside of a GCP environment, you may need
# to specify the path to a service account key file.
# GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "path/to/your/keyfile.json")
