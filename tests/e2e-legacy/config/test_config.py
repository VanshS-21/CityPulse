"""
Test configuration for CityPulse E2E test suite.

This module contains all configuration settings, constants, and environment
variables needed for running the E2E tests.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class GCPConfig:
    """Google Cloud Platform configuration."""
    project_id: str
    region: str
    temp_bucket: str
    service_account_key_path: str = None


@dataclass
class PubSubConfig:
    """Pub/Sub configuration."""
    citizen_reports_topic: str = "citypulse-citizen_reports"
    iot_data_topic: str = "citypulse-iot_data"
    ai_processing_topic: str = "citypulse-ai_processing"
    
    # Test-specific topics (will be created/destroyed during tests)
    test_topic_prefix: str = "test-citypulse"


@dataclass
class BigQueryConfig:
    """BigQuery configuration."""
    dataset_id: str = "citypulse_analytics"
    
    # Main tables
    events_table: str = "events"
    citizen_reports_table: str = "citizen_reports"
    iot_data_table: str = "iot_data"
    ai_processing_results_table: str = "ai_processing_results"
    
    # Dead letter tables
    dead_letter_events_table: str = "dead_letter_events"
    dead_letter_citizen_reports_table: str = "dead_letter_citizen_reports"
    dead_letter_iot_data_table: str = "dead_letter_iot_data"
    
    # Test-specific tables (will be created/destroyed during tests)
    test_table_prefix: str = "test_"


@dataclass
class DataflowConfig:
    """Dataflow configuration."""
    region: str
    temp_location: str
    staging_location: str
    max_num_workers: int = 3
    machine_type: str = "n1-standard-1"
    
    # Pipeline templates
    citizen_reports_template: str = "citizen-reports-ingestion"
    iot_data_template: str = "iot-data-ingestion"
    ai_processing_template: str = "ai-processing-pipeline"


@dataclass
class TestConfig:
    """Main test configuration."""
    # Test execution settings
    default_timeout: int = 300  # 5 minutes
    pipeline_timeout: int = 600  # 10 minutes
    cleanup_timeout: int = 120   # 2 minutes
    
    # Test data settings
    sample_events_count: int = 10
    invalid_events_count: int = 3
    performance_events_count: int = 100
    
    # Validation settings
    max_retry_attempts: int = 3
    retry_delay: int = 10  # seconds
    
    # Resource naming
    resource_prefix: str = "e2e-test"
    unique_suffix_length: int = 8


def get_gcp_config() -> GCPConfig:
    """Get GCP configuration from environment variables."""
    from ..utils.environment_helpers import get_gcp_config_from_env

    config = get_gcp_config_from_env()
    return GCPConfig(
        project_id=config["project_id"],
        region=config["region"],
        temp_bucket=config["temp_bucket"],
        service_account_key_path=config["service_account_key_path"]
    )


def get_pubsub_config() -> PubSubConfig:
    """Get Pub/Sub configuration."""
    return PubSubConfig()


def get_bigquery_config() -> BigQueryConfig:
    """Get BigQuery configuration."""
    return BigQueryConfig()


def get_dataflow_config(gcp_config: GCPConfig) -> DataflowConfig:
    """Get Dataflow configuration."""
    temp_location = f"gs://{gcp_config.temp_bucket}/dataflow/temp"
    staging_location = f"gs://{gcp_config.temp_bucket}/dataflow/staging"
    
    return DataflowConfig(
        region=gcp_config.region,
        temp_location=temp_location,
        staging_location=staging_location
    )


def get_test_config() -> TestConfig:
    """Get test configuration."""
    return TestConfig()


def get_all_configs() -> Dict[str, Any]:
    """Get all configurations as a dictionary."""
    gcp_config = get_gcp_config()
    
    return {
        "gcp": gcp_config,
        "pubsub": get_pubsub_config(),
        "bigquery": get_bigquery_config(),
        "dataflow": get_dataflow_config(gcp_config),
        "test": get_test_config()
    }


# Import consolidated environment validation
from ..utils.environment_helpers import validate_required_environment_variables

# Environment validation
def validate_environment():
    """Validate that all required environment variables are set."""
    return validate_required_environment_variables(exit_on_failure=False, print_instructions=False)


# Test data schemas - Updated to match actual BigQuery table schemas
CITIZEN_REPORT_SCHEMA = {
    "event_id": "string",
    "title": "string",
    "description": "string",
    "location": "geography",  # Updated to match actual table schema
    "start_time": "timestamp",
    "end_time": "timestamp",
    "category": "string",
    "severity": "string",
    "source": "string",
    "status": "string",
    "user_id": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "metadata": "json",
    "ai_summary": "string",
    "ai_category": "string",
    "ai_image_tags": "string",  # REPEATED fields show as STRING in schema
    "ai_generated_image_url": "string",
    "image_url": "string",
    "maps_url": "string"
}

IOT_DATA_SCHEMA = {
    "device_id": "string",
    "sensor_type": "string",
    "measurement_value": "float",
    "measurement_unit": "string",
    "location": "object",
    "timestamp": "timestamp",
    "quality_score": "float"
}

AI_PROCESSING_SCHEMA = {
    "event_id": "string",
    "ai_summary": "string",
    "ai_category": "string",
    "ai_image_tags": "array",
    "ai_generated_image_url": "string",
    "processing_timestamp": "timestamp",
    "confidence_score": "float"
}

# Dead letter table schema - matches actual BigQuery table
DEAD_LETTER_SCHEMA = {
    "timestamp": "timestamp",
    "pipeline_step": "string",
    "raw_data": "string",
    "error_message": "string"
}
