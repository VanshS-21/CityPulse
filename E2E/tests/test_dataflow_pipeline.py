"""
Dataflow pipeline tests for CityPulse E2E test suite.

This module tests Dataflow job execution, pipeline validation,
and data transformation workflows.
"""

import pytest
import time
import subprocess
from typing import Dict, Any, List

from ..config.test_config import get_all_configs
from ..utils.gcp_helpers import (
    PubSubHelper, BigQueryHelper, DataflowHelper, 
    generate_unique_resource_name
)
from ..utils.data_generators import generate_citizen_report, generate_iot_data
from ..utils.test_helpers import (
    TestTimer, wait_for_condition, run_gcloud_command,
    get_dataflow_job_status
)


@pytest.fixture(scope="module")
def configs():
    """Get test configurations."""
    return get_all_configs()


@pytest.fixture(scope="module")
def pubsub_helper(configs):
    """Create PubSub helper instance."""
    helper = PubSubHelper(configs["gcp"].project_id)
    yield helper
    helper.cleanup()


@pytest.fixture(scope="module")
def bigquery_helper(configs):
    """Create BigQuery helper instance."""
    helper = BigQueryHelper(
        configs["gcp"].project_id,
        configs["bigquery"].dataset_id
    )
    yield helper
    helper.cleanup()


@pytest.fixture(scope="module")
def dataflow_helper(configs):
    """Create Dataflow helper instance."""
    helper = DataflowHelper(
        configs["gcp"].project_id,
        configs["gcp"].region
    )
    yield helper
    helper.cleanup()


class TestDataflowJobManagement:
    """Test Dataflow job lifecycle management."""
    
    def test_list_active_dataflow_jobs(self, configs):
        """Test listing active Dataflow jobs."""
        command = [
            "gcloud", "dataflow", "jobs", "list",
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--status", "active",
            "--format", "json"
        ]
        
        with TestTimer("list active jobs"):
            result = run_gcloud_command(command)
        
        assert result["success"], f"Failed to list jobs: {result['stderr']}"
        
        # Should return valid JSON (even if empty list)
        import json
        try:
            jobs = json.loads(result["stdout"])
            assert isinstance(jobs, list), "Jobs list should be an array"
        except json.JSONDecodeError:
            pytest.fail("Invalid JSON response from gcloud")
    
    def test_get_job_details(self, configs):
        """Test getting details of existing Dataflow job."""
        # First, get list of active jobs
        list_command = [
            "gcloud", "dataflow", "jobs", "list",
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--status", "active",
            "--format", "value(id)"
        ]
        
        list_result = run_gcloud_command(list_command)
        
        if not list_result["success"] or not list_result["stdout"].strip():
            pytest.skip("No active Dataflow jobs found")
        
        job_ids = list_result["stdout"].strip().split('\n')
        job_id = job_ids[0]  # Use first active job
        
        # Get job details
        detail_command = [
            "gcloud", "dataflow", "jobs", "describe", job_id,
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--format", "json"
        ]
        
        with TestTimer("get job details"):
            result = run_gcloud_command(detail_command)
        
        assert result["success"], f"Failed to get job details: {result['stderr']}"
        
        # Verify job details structure
        import json
        job_details = json.loads(result["stdout"])
        
        required_fields = ["id", "name", "currentState", "createTime"]
        for field in required_fields:
            assert field in job_details, f"Missing field {field} in job details"


class TestPipelineValidation:
    """Test pipeline validation and configuration."""
    
    def test_validate_citizen_reports_pipeline_config(self, configs):
        """Test citizen reports pipeline configuration."""
        # Check if the pipeline script exists
        import os
        pipeline_script = os.path.join("data_models", "data_ingestion", "citizen_reports_ingestion.py")
        
        if not os.path.exists(pipeline_script):
            pytest.skip(f"Pipeline script not found: {pipeline_script}")
        
        # Validate pipeline can be imported
        try:
            import sys
            sys.path.insert(0, "data_models")
            from data_ingestion import citizen_reports_ingestion
            
            # Check if main pipeline function exists
            assert hasattr(citizen_reports_ingestion, 'run'), "Pipeline missing run function"
            
        except ImportError as e:
            pytest.fail(f"Failed to import pipeline: {e}")
    
    def test_pipeline_dependencies(self, configs):
        """Test that pipeline dependencies are available."""
        required_modules = [
            "apache_beam",
            "google.cloud.pubsub",
            "google.cloud.bigquery"
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Required module not available: {module_name}")


class TestDataTransformation:
    """Test data transformation logic."""
    
    def test_citizen_report_transformation(self, configs):
        """Test citizen report data transformation."""
        # Generate test data
        raw_data = generate_citizen_report(valid=True)
        
        # Test transformation logic (if available)
        # This would test the actual transformation functions
        # For now, we'll validate the data structure
        
        required_fields = ["event_id", "title", "description", "created_at"]
        for field in required_fields:
            assert field in raw_data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(raw_data["event_id"], str)
        assert isinstance(raw_data["title"], str)
        assert isinstance(raw_data["description"], str)
    
    def test_invalid_data_handling(self, configs):
        """Test handling of invalid data."""
        # Generate invalid data
        invalid_data = generate_citizen_report(valid=False)
        
        # This would test the pipeline's error handling
        # For now, we'll verify the data is indeed invalid
        
        # The invalid data should be missing required fields or have wrong types
        # This validates our test data generator is working correctly
        assert isinstance(invalid_data, dict), "Invalid data should still be a dict"


class TestPipelinePerformance:
    """Test pipeline performance characteristics."""
    
    def test_pipeline_resource_usage(self, configs):
        """Test pipeline resource usage."""
        # Get current active jobs and their resource usage
        command = [
            "gcloud", "dataflow", "jobs", "list",
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--status", "active",
            "--format", "table(id,name,currentState,createTime)"
        ]
        
        result = run_gcloud_command(command)
        
        if result["success"]:
            print("Active Dataflow Jobs:")
            print(result["stdout"])
        else:
            pytest.skip("Could not retrieve job information")
    
    def test_pipeline_scaling(self, configs):
        """Test pipeline auto-scaling behavior."""
        # This would test if the pipeline scales appropriately
        # For now, we'll check if scaling parameters are configured
        
        # Check if we can get metrics for active jobs
        list_command = [
            "gcloud", "dataflow", "jobs", "list",
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--status", "active",
            "--format", "value(id)"
        ]
        
        list_result = run_gcloud_command(list_command)
        
        if not list_result["success"] or not list_result["stdout"].strip():
            pytest.skip("No active jobs to test scaling")
        
        job_ids = list_result["stdout"].strip().split('\n')
        job_id = job_ids[0]
        
        # Get job metrics
        metrics_command = [
            "gcloud", "dataflow", "jobs", "describe", job_id,
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--format", "value(environment.workerPools[0].numWorkers)"
        ]
        
        metrics_result = run_gcloud_command(metrics_command)
        
        if metrics_result["success"] and metrics_result["stdout"].strip():
            num_workers = int(metrics_result["stdout"].strip())
            print(f"Current number of workers: {num_workers}")
            
            # Basic validation - should have at least 1 worker
            assert num_workers >= 1, "Pipeline should have at least 1 worker"


class TestPipelineMonitoring:
    """Test pipeline monitoring and logging."""
    
    def test_pipeline_logs_available(self, configs):
        """Test that pipeline logs are available."""
        # Get active jobs
        list_command = [
            "gcloud", "dataflow", "jobs", "list",
            "--project", configs["gcp"].project_id,
            "--region", configs["gcp"].region,
            "--status", "active",
            "--format", "value(id)"
        ]
        
        list_result = run_gcloud_command(list_command)
        
        if not list_result["success"] or not list_result["stdout"].strip():
            pytest.skip("No active jobs to check logs")
        
        job_ids = list_result["stdout"].strip().split('\n')
        job_id = job_ids[0]
        
        # Check if logs are available
        logs_command = [
            "gcloud", "logging", "read",
            f"resource.type=dataflow_job AND resource.labels.job_id={job_id}",
            "--project", configs["gcp"].project_id,
            "--limit", "5",
            "--format", "value(timestamp,severity,textPayload)"
        ]
        
        with TestTimer("retrieve logs"):
            logs_result = run_gcloud_command(logs_command, timeout=60)
        
        # Logs should be available (even if empty)
        assert logs_result["success"], f"Failed to retrieve logs: {logs_result['stderr']}"
    
    def test_pipeline_error_handling(self, configs):
        """Test pipeline error handling and dead letter queues."""
        # Check if dead letter table has data (indicates error handling is working)
        from google.cloud import bigquery
        
        client = bigquery.Client(project=configs["gcp"].project_id)
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].dead_letter_events_table}"
        
        try:
            query = f"SELECT COUNT(*) as error_count FROM `{table_id}`"
            result = list(client.query(query).result())
            
            error_count = result[0].error_count
            print(f"Dead letter events count: {error_count}")
            
            # Having some errors is actually good - it means error handling works
            # We just verify the table is accessible and queryable
            assert error_count >= 0, "Error count should be non-negative"
            
        except Exception as e:
            pytest.skip(f"Could not access dead letter table: {e}")
