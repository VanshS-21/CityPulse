#!/bin/bash

# Import existing resources into Terraform state

echo "Importing existing Pub/Sub topics..."
terraform import 'google_pubsub_topic.topics["official_feeds"]' projects/citypulse-21/topics/citypulse-official_feeds-ingestion
terraform import 'google_pubsub_topic.topics["iot_sensors"]' projects/citypulse-21/topics/citypulse-iot_sensors-ingestion

echo "Importing existing BigQuery dataset..."
terraform import google_bigquery_dataset.analytics citypulse-21:citypulse_analytics

echo "Importing existing storage buckets..."
terraform import google_storage_bucket.tf_state citypulse-tf-state
terraform import google_storage_bucket.audit_logs citypulse-21-security-audit-logs

echo "Importing existing service accounts..."
terraform import google_service_account.citypulse_sa projects/citypulse-21/serviceAccounts/citypulse-sa@citypulse-21.iam.gserviceaccount.com
terraform import google_service_account.dataflow_worker projects/citypulse-21/serviceAccounts/citypulse-dataflow-worker@citypulse-21.iam.gserviceaccount.com
terraform import google_service_account.ai_processor projects/citypulse-21/serviceAccounts/citypulse-ai-processor@citypulse-21.iam.gserviceaccount.com
terraform import google_service_account.api_service projects/citypulse-21/serviceAccounts/citypulse-api-service@citypulse-21.iam.gserviceaccount.com

echo "Importing existing IAM custom roles..."
terraform import google_project_iam_custom_role.citizen_report_processor projects/citypulse-21/roles/citizenReportProcessor
terraform import google_project_iam_custom_role.ai_data_processor projects/citypulse-21/roles/aiDataProcessor
terraform import google_project_iam_custom_role.api_service_role projects/citypulse-21/roles/apiServiceRole

echo "Importing existing network resources..."
terraform import google_compute_network.citypulse_vpc projects/citypulse-21/global/networks/citypulse-private-network

echo "Importing existing KMS keyring..."
terraform import google_kms_key_ring.citypulse_keyring projects/citypulse-21/locations/us-central1/keyRings/citypulse-keyring

echo "Importing additional existing resources..."

# Import BigQuery datasets
terraform import google_bigquery_dataset.citypulse_analytics_optimized citypulse-21:citypulse_analytics_optimized

# Import network components
terraform import google_compute_subnetwork.dataflow_subnet projects/citypulse-21/regions/us-central1/subnetworks/citypulse-dataflow-subnet
terraform import google_compute_subnetwork.api_subnet projects/citypulse-21/regions/us-central1/subnetworks/citypulse-api-subnet

# Import firewall rules
terraform import google_compute_firewall.dataflow_internal projects/citypulse-21/global/firewalls/citypulse-dataflow-internal
terraform import google_compute_firewall.api_internal projects/citypulse-21/global/firewalls/citypulse-api-internal
terraform import google_compute_firewall.deny_all_ingress projects/citypulse-21/global/firewalls/citypulse-deny-all-ingress

# Import router
terraform import google_compute_router.citypulse_router projects/citypulse-21/regions/us-central1/routers/citypulse-router

# Import KMS keys
terraform import google_kms_crypto_key.dataflow_key projects/citypulse-21/locations/us-central1/keyRings/citypulse-keyring/cryptoKeys/citypulse-dataflow-key
terraform import google_kms_crypto_key.storage_key projects/citypulse-21/locations/us-central1/keyRings/citypulse-keyring/cryptoKeys/citypulse-storage-key

echo "Import completed!"
