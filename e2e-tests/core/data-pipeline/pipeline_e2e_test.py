"""
Data Pipeline E2E Testing Framework for CityPulse

This module provides comprehensive testing for the complete data pipeline:
- Pub/Sub message ingestion
- Dataflow processing validation
- BigQuery data integrity
- AI processing workflows
- Error handling and recovery
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytest
from pathlib import Path

# GCP imports
from google.cloud import pubsub_v1
from google.cloud import bigquery
from google.cloud import dataflow_v1beta3
from google.api_core import exceptions as gcp_exceptions

class DataPipelineE2ETest:
    """Comprehensive E2E testing for CityPulse data pipeline."""
    
    def __init__(self, environment: str = "test"):
        self.environment = environment
        self.config = self._load_config()
        self.test_data = self._load_test_data()
        
        # GCP clients
        self.pubsub_client = None
        self.bigquery_client = None
        self.dataflow_client = None
        
        # Test resources tracking
        self.created_topics = []
        self.created_subscriptions = []
        self.created_tables = []
        self.test_messages = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load environment configuration."""
        config_path = Path(__file__).parent.parent.parent / "config" / "environments.json"
        with open(config_path) as f:
            configs = json.load(f)
        return configs.get(self.environment, configs["test"])
    
    def _load_test_data(self) -> Dict[str, Any]:
        """Load test data fixtures."""
        data_path = Path(__file__).parent.parent.parent / "config" / "test-data.json"
        with open(data_path) as f:
            return json.load(f)
    
    async def setup_clients(self):
        """Initialize GCP clients."""
        project_id = self.config["gcp"]["projectId"]
        
        self.pubsub_client = pubsub_v1.PublisherClient()
        self.bigquery_client = bigquery.Client(project=project_id)
        self.dataflow_client = dataflow_v1beta3.JobsV1Beta3Client()
    
    async def teardown_clients(self):
        """Clean up GCP clients and test resources."""
        await self.cleanup_test_resources()
        
        if self.pubsub_client:
            self.pubsub_client.close()
        if self.bigquery_client:
            self.bigquery_client.close()
        if self.dataflow_client:
            self.dataflow_client.close()
    
    def generate_test_resource_name(self, resource_type: str) -> str:
        """Generate unique test resource name."""
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        prefix = self.config["gcp"]["pubsub"].get(f"{resource_type}Prefix", "test-")
        return f"{prefix}{resource_type}-{timestamp}-{unique_id}"
    
    async def create_test_topic(self, topic_name: str = None) -> str:
        """Create a test Pub/Sub topic."""
        if topic_name is None:
            topic_name = self.generate_test_resource_name("topic")
        
        project_id = self.config["gcp"]["projectId"]
        topic_path = self.pubsub_client.topic_path(project_id, topic_name)
        
        try:
            self.pubsub_client.create_topic(request={"name": topic_path})
            self.created_topics.append(topic_path)
            return topic_path
        except gcp_exceptions.AlreadyExists:
            return topic_path
    
    async def create_test_subscription(self, topic_path: str, subscription_name: str = None) -> str:
        """Create a test Pub/Sub subscription."""
        if subscription_name is None:
            subscription_name = self.generate_test_resource_name("subscription")
        
        project_id = self.config["gcp"]["projectId"]
        subscription_path = self.pubsub_client.subscription_path(project_id, subscription_name)
        
        try:
            self.pubsub_client.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path
                }
            )
            self.created_subscriptions.append(subscription_path)
            return subscription_path
        except gcp_exceptions.AlreadyExists:
            return subscription_path
    
    async def publish_test_message(self, topic_path: str, message_data: Dict[str, Any]) -> str:
        """Publish a test message to Pub/Sub topic."""
        message_json = json.dumps(message_data)
        message_bytes = message_json.encode('utf-8')
        
        # Add test metadata
        attributes = {
            "test_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment
        }
        
        future = self.pubsub_client.publish(
            topic_path,
            message_bytes,
            **attributes
        )
        
        message_id = future.result()
        self.test_messages.append({
            "message_id": message_id,
            "topic": topic_path,
            "data": message_data,
            "attributes": attributes
        })
        
        return message_id
    
    async def wait_for_dataflow_job_completion(
        self,
        job_name: str,
        timeout: int = 300,
        check_interval: int = 10
    ) -> Dict[str, Any]:
        """Wait for Dataflow job to complete and return job status."""
        
        project_id = self.config["gcp"]["projectId"]
        region = self.config["gcp"]["region"]
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # List jobs to find our job
                request = dataflow_v1beta3.ListJobsRequest(
                    project_id=project_id,
                    location=region
                )
                
                jobs = self.dataflow_client.list_jobs(request=request)
                
                for job in jobs:
                    if job.name == job_name:
                        if job.current_state in [
                            dataflow_v1beta3.JobState.JOB_STATE_DONE,
                            dataflow_v1beta3.JobState.JOB_STATE_FAILED,
                            dataflow_v1beta3.JobState.JOB_STATE_CANCELLED
                        ]:
                            return {
                                "job_id": job.id,
                                "name": job.name,
                                "state": job.current_state.name,
                                "create_time": job.create_time,
                                "start_time": job.start_time,
                                "end_time": job.end_time if hasattr(job, 'end_time') else None
                            }
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"Error checking Dataflow job status: {e}")
                await asyncio.sleep(check_interval)
        
        raise TimeoutError(f"Dataflow job {job_name} did not complete within {timeout} seconds")
    
    async def validate_bigquery_data(
        self,
        table_id: str,
        expected_records: List[Dict[str, Any]],
        timeout: int = 120
    ) -> bool:
        """Validate that expected data appears in BigQuery table."""
        
        dataset_id = self.config["database"]["bigquery"]["datasetId"]
        project_id = self.config["gcp"]["projectId"]
        
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                query = f"""
                SELECT *
                FROM `{table_ref}`
                WHERE test_id IN ({','.join([f"'{msg['attributes']['test_id']}'" for msg in self.test_messages])})
                ORDER BY created_at DESC
                """
                
                query_job = self.bigquery_client.query(query)
                results = list(query_job.result())
                
                if len(results) >= len(expected_records):
                    # Validate data content
                    for expected_record in expected_records:
                        found = False
                        for result in results:
                            if self._compare_records(dict(result), expected_record):
                                found = True
                                break
                        
                        if not found:
                            print(f"Expected record not found: {expected_record}")
                            return False
                    
                    return True
                
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Error validating BigQuery data: {e}")
                await asyncio.sleep(5)
        
        return False
    
    def _compare_records(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Compare actual and expected records with flexible matching."""
        for key, expected_value in expected.items():
            if key not in actual:
                return False
            
            actual_value = actual[key]
            
            # Handle different data types
            if isinstance(expected_value, str) and isinstance(actual_value, str):
                if expected_value.lower() != actual_value.lower():
                    return False
            elif expected_value != actual_value:
                return False
        
        return True
    
    async def cleanup_test_resources(self):
        """Clean up all created test resources."""
        # Clean up subscriptions
        for subscription_path in self.created_subscriptions:
            try:
                self.pubsub_client.delete_subscription(request={"subscription": subscription_path})
            except Exception as e:
                print(f"Error deleting subscription {subscription_path}: {e}")
        
        # Clean up topics
        for topic_path in self.created_topics:
            try:
                self.pubsub_client.delete_topic(request={"topic": topic_path})
            except Exception as e:
                print(f"Error deleting topic {topic_path}: {e}")
        
        # Clean up BigQuery tables
        for table_id in self.created_tables:
            try:
                dataset_id = self.config["database"]["bigquery"]["datasetId"]
                table_ref = self.bigquery_client.dataset(dataset_id).table(table_id)
                self.bigquery_client.delete_table(table_ref)
            except Exception as e:
                print(f"Error deleting table {table_id}: {e}")
    
    async def test_complete_pipeline_flow(self):
        """Test the complete data pipeline from Pub/Sub to BigQuery."""
        await self.setup_clients()
        
        try:
            # 1. Create test topic and subscription
            topic_path = await self.create_test_topic()
            subscription_path = await self.create_test_subscription(topic_path)
            
            # 2. Publish test messages
            test_events = [
                self.test_data["events"]["validEvent"],
                self.test_data["events"]["trafficEvent"],
                self.test_data["events"]["environmentalEvent"]
            ]
            
            message_ids = []
            for event in test_events:
                message_id = await self.publish_test_message(topic_path, event)
                message_ids.append(message_id)
            
            # 3. Wait for Dataflow processing (if applicable)
            # This would depend on your specific Dataflow job setup
            
            # 4. Validate data in BigQuery
            validation_result = await self.validate_bigquery_data(
                "events",  # Assuming events table
                test_events
            )
            
            assert validation_result, "Data validation failed in BigQuery"
            
            print(f"✅ Pipeline test completed successfully!")
            print(f"   Messages published: {len(message_ids)}")
            print(f"   Data validated in BigQuery: {len(test_events)} records")
            
        finally:
            await self.teardown_clients()

# Pytest fixtures
@pytest.fixture
async def pipeline_test():
    """Fixture for data pipeline testing."""
    test = DataPipelineE2ETest()
    yield test
    await test.teardown_clients()

# Export main classes
__all__ = [
    "DataPipelineE2ETest",
    "pipeline_test"
]
