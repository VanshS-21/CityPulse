"""Environment validation utilities for E2E tests."""

import os
import sys
from typing import List, Optional


def validate_required_environment_variables(
    required_vars: Optional[List[str]] = None,
    exit_on_failure: bool = True,
    print_instructions: bool = True
) -> bool:
    """
    Validate that all required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names.
                      Defaults to standard GCP variables.
        exit_on_failure: Whether to exit the program if validation fails.
        print_instructions: Whether to print setup instructions on failure.
    
    Returns:
        bool: True if all variables are set, False otherwise.
    
    Raises:
        EnvironmentError: If exit_on_failure is False and variables are missing.
    """
    if required_vars is None:
        required_vars = [
            "GCP_PROJECT_ID",
            "GCP_REGION", 
            "GCP_TEMP_BUCKET"
        ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        
        if print_instructions:
            if exit_on_failure:
                print(f"❌ {error_msg}")
                print("\nPlease set these variables before running tests:")
                print("export GCP_PROJECT_ID='citypulse-21'")
                print("export GCP_REGION='us-central1'")
                print("export GCP_TEMP_BUCKET='citypulse-dataflow-temp'")
            
        if exit_on_failure:
            sys.exit(1)
        else:
            raise EnvironmentError(f"{error_msg}\nPlease set these variables before running tests.")
    
    if print_instructions:
        print("✅ Environment variables validated")
    
    return True


def get_environment_variable(var_name: str, default: Optional[str] = None) -> str:
    """
    Get an environment variable with optional default.

    Args:
        var_name: Name of the environment variable.
        default: Default value if variable is not set.

    Returns:
        str: The environment variable value.

    Raises:
        EnvironmentError: If variable is not set and no default provided.
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set")
    return value


def get_gcp_config_from_env() -> dict:
    """
    Get standardized GCP configuration from environment variables.

    Returns:
        dict: Dictionary containing GCP configuration values.
    """
    return {
        "project_id": get_environment_variable("GCP_PROJECT_ID", "citypulse-21"),
        "region": get_environment_variable("GCP_REGION", "us-central1"),
        "temp_bucket": get_environment_variable("GCP_TEMP_BUCKET", "citypulse-dataflow-temp"),
        "service_account_key_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    }


def get_bigquery_config_from_env() -> dict:
    """
    Get standardized BigQuery configuration from environment variables.

    Returns:
        dict: Dictionary containing BigQuery configuration values.
    """
    gcp_config = get_gcp_config_from_env()
    return {
        "project_id": gcp_config["project_id"],
        "dataset": get_environment_variable("BIGQUERY_DATASET", "citypulse_analytics"),
        "events_table": get_environment_variable("BIGQUERY_EVENTS_TABLE", "events"),
        "dead_letter_table": get_environment_variable("BIGQUERY_DEAD_LETTER_TABLE", "dead_letter_events")
    }


def get_pubsub_config_from_env() -> dict:
    """
    Get standardized Pub/Sub configuration from environment variables.

    Returns:
        dict: Dictionary containing Pub/Sub configuration values.
    """
    gcp_config = get_gcp_config_from_env()
    return {
        "project_id": gcp_config["project_id"],
        "citizen_reports_topic": get_environment_variable("PUBSUB_CITIZEN_REPORTS_TOPIC", "citypulse-citizen_reports"),
        "iot_data_topic": get_environment_variable("PUBSUB_IOT_DATA_TOPIC", "citypulse-iot_data")
    }
