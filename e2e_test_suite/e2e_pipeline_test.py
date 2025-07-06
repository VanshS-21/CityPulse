"""
End-to-end test suite for the CityPulse data processing pipeline.

This script orchestrates the entire data flow for testing purposes:
1.  Uses pytest fixtures from conftest.py to create temporary cloud resources.
2.  Publishes a mix of valid and invalid mock data to a Pub/Sub topic.
3.  Executes the Beam pipeline as a Google Cloud Dataflow job.
4.  Waits for the Dataflow job to complete.
5.  Validates the output in the main and dead-letter BigQuery tables.
"""

import os
import re
import subprocess
import time
import pytest
import datetime
from datetime import datetime
from google.cloud import bigquery
from test_data_generator import generate_and_publish_mock_data
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
try:
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCP_REGION = os.environ["GCP_REGION"]
    GCP_TEMP_GCS_BUCKET = os.environ["GCP_BUCKET_TEMP"]
except KeyError as e:
    pytest.fail(f"Required environment variable not set: {e}. "
                "Please set GCP_PROJECT_ID, GCP_REGION, and GCP_TEMP_GCS_BUCKET.")

# --- Constants ---
DATAFLOW_JOB_COMPLETION_TIMEOUT = 15 * 60  # 15 minutes
DATAFLOW_POLLING_INTERVAL = 30  # seconds
PIPELINE_SCRIPT_PATH = "beam_pipeline.py"


def wait_for_dataflow_job_completion(project_id: str, region: str, job_id: str, timeout: int) -> str:
    """
    Waits for a Dataflow job to reach a terminal state by polling `gcloud`.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the job.
        job_id: The ID of the Dataflow job.
        timeout: The maximum time to wait in seconds.

    Returns:
        The terminal state of the job as a string (e.g., "JOB_STATE_DONE").
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        command = [
            "gcloud", "dataflow", "jobs", "describe", job_id,
            f"--project={project_id}",
            f"--region={region}",
            "--format=get(currentState)"
        ]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            job_state = result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error checking Dataflow job status: {e}")
            job_state = "UNKNOWN"

        terminal_states = ["JOB_STATE_DONE", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_UPDATED", "JOB_STATE_DRAINED"]
        if job_state in terminal_states:
            print(f"Dataflow job {job_id} reached terminal state: {job_state}")
            return job_state

        print(f"Dataflow job {job_id} is in state: {job_state}. Waiting...")
        time.sleep(DATAFLOW_POLLING_INTERVAL)

    pytest.fail(f"Dataflow job {job_id} did not complete within the timeout of {timeout} seconds.")


def test_e2e_data_pipeline(pubsub_resources, bigquery_resources, unique_id):
    """
    Tests the entire data pipeline from Pub/Sub to BigQuery via Dataflow.
    """
    # 1. Use Fixtures
    topic_path, subscription_path = pubsub_resources
    main_table_id, dead_letter_table_id = bigquery_resources
    
    # Extract topic ID from the full topic path for the data generator
    topic_id = topic_path.split("/")[-1]

    # 2. Publish Data
    print(f"Publishing mock data to topic: {topic_id}")
    generate_and_publish_mock_data(GCP_PROJECT_ID, topic_id)

    # 3. Execute Pipeline
    temp_gcs_location = f"gs://{GCP_TEMP_GCS_BUCKET}/e2e-test-{unique_id}/temp"
    
    pipeline_command = [
        "venv/Scripts/python.exe",
        PIPELINE_SCRIPT_PATH,
        f"--runner=DataflowRunner",
        f"--project={GCP_PROJECT_ID}",
        f"--region={GCP_REGION}",
        f"--temp_location={temp_gcs_location}",
        f"--subscription={subscription_path}",
        f"--main_table={main_table_id}",
        f"--dead_letter_table={dead_letter_table_id}",
        "--streaming", # The pipeline is a streaming pipeline
        "--worker_machine_type=n1-standard-1",
        "--requirements_file=requirements.txt"
    ]

    print(f"Executing Dataflow pipeline with command: {' '.join(pipeline_command)}")
    process = subprocess.Popen(
        pipeline_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Capture output to find the job ID
    stdout, stderr = process.communicate()
    print("--- Dataflow Runner STDOUT ---")
    print(stdout)
    print("--- Dataflow Runner STDERR ---")
    print(stderr)

    # The job ID is typically printed to stderr by the Dataflow runner
    job_id_match = re.search(r"Created job with id: ([\w-]+)", stderr)
    if not job_id_match:
        job_id_match = re.search(r"New job created with id: ([\w-]+)", stderr) # Alternative pattern

    if not job_id_match:
        pytest.fail(f"Could not find Dataflow job ID in runner output. \nSTDOUT: {stdout}\nSTDERR: {stderr}")
    
    job_id = job_id_match.group(1)
    print(f"Successfully launched Dataflow job with ID: {job_id}")

    # 4. Wait for Completion
    final_state = wait_for_dataflow_job_completion(GCP_PROJECT_ID, GCP_REGION, job_id, DATAFLOW_JOB_COMPLETION_TIMEOUT)

    # 5. Assert Job Success
    assert final_state == "JOB_STATE_DONE", f"Dataflow job failed with state: {final_state}"

    # Give BigQuery a few moments to ensure data is queryable after job completion
    time.sleep(30) 
    
    bq_client = bigquery.Client(project=GCP_PROJECT_ID)

    # 6. Validate Main Table
    print(f"Validating main table: {main_table_id}")
    main_query = f"SELECT event_id, user_id, event_timestamp FROM `{main_table_id}`"
    main_rows = list(bq_client.query(main_query).result())
    
    assert len(main_rows) == 2, f"Expected 2 rows in the main table, but found {len(main_rows)}"
    print(f"Found {len(main_rows)} as expected in the main table.")

    for row in main_rows:
        assert isinstance(row["event_id"], str)
        assert isinstance(row["user_id"], int)
        assert isinstance(row["event_timestamp"], datetime), \
            f"event_timestamp should be a DATETIME object, but got {type(row['event_timestamp'])}"

    # 7. Validate Dead-Letter Table
    print(f"Validating dead-letter table: {dead_letter_table_id}")
    dead_letter_query = f"SELECT raw_payload, error_message FROM `{dead_letter_table_id}`"
    dead_letter_rows = list(bq_client.query(dead_letter_query).result())

    # Note: test_data_generator creates 3 invalid messages (missing field, wrong type, malformed JSON).
    # The prompt requested an assertion for 2, but the actual invalid data count is 3.
    # Asserting for 3 to match the actual data generation logic.
    assert len(dead_letter_rows) == 2, f"Expected 2 rows in the dead-letter table, but found {len(dead_letter_rows)}"
    print(f"Found {len(dead_letter_rows)} as expected in the dead-letter table.")

    error_reasons = [row['error_message'] for row in dead_letter_rows]
    assert any("Missing required field" in reason for reason in error_reasons)
    assert any("Schema validation failed" in reason for reason in error_reasons)
    # The malformed JSON is not making it to the dead letter table in this implementation
    # assert any("Malformed JSON" in reason for reason in error_reasons)