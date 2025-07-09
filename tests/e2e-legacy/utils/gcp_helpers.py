"""
Google Cloud Platform helper utilities for E2E tests.

This module provides utilities for managing GCP resources during testing,
including Pub/Sub topics, BigQuery tables, and Dataflow jobs.
"""

import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from google.cloud import pubsub_v1, bigquery
from google.cloud.exceptions import NotFound, Conflict
from google.api_core import retry
import logging

logger = logging.getLogger(__name__)


class PubSubHelper:
    """Helper class for managing Pub/Sub resources during tests."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.created_topics = []
        self.created_subscriptions = []
    
    def create_test_topic(self, topic_name: str) -> str:
        """
        Create a test topic.
        
        Args:
            topic_name: Name of the topic to create
            
        Returns:
            Full topic path
        """
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        
        try:
            self.publisher.create_topic(request={"name": topic_path})
            self.created_topics.append(topic_path)
            logger.info(f"Created topic: {topic_path}")
        except Conflict:
            logger.info(f"Topic already exists: {topic_path}")
        
        return topic_path
    
    def create_test_subscription(self, topic_path: str, subscription_name: str) -> str:
        """
        Create a test subscription.
        
        Args:
            topic_path: Full path of the topic
            subscription_name: Name of the subscription to create
            
        Returns:
            Full subscription path
        """
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_name
        )
        
        try:
            self.subscriber.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path
                }
            )
            self.created_subscriptions.append(subscription_path)
            logger.info(f"Created subscription: {subscription_path}")
        except Conflict:
            logger.info(f"Subscription already exists: {subscription_path}")
        
        return subscription_path
    
    def publish_messages(self, topic_path: str, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Publish messages to a topic.
        
        Args:
            topic_path: Full path of the topic
            messages: List of message dictionaries
            
        Returns:
            List of message IDs
        """
        import json
        
        message_ids = []
        for message in messages:
            data = json.dumps(message).encode('utf-8')
            future = self.publisher.publish(topic_path, data)
            message_id = future.result()
            message_ids.append(message_id)
        
        logger.info(f"Published {len(messages)} messages to {topic_path}")
        return message_ids
    
    def cleanup(self):
        """Clean up all created resources."""
        # Delete subscriptions first
        for subscription_path in self.created_subscriptions:
            try:
                self.subscriber.delete_subscription(
                    request={"subscription": subscription_path}
                )
                logger.info(f"Deleted subscription: {subscription_path}")
            except NotFound:
                logger.warning(f"Subscription not found during cleanup: {subscription_path}")
        
        # Then delete topics
        for topic_path in self.created_topics:
            try:
                self.publisher.delete_topic(request={"topic": topic_path})
                logger.info(f"Deleted topic: {topic_path}")
            except NotFound:
                logger.warning(f"Topic not found during cleanup: {topic_path}")
        
        self.created_topics.clear()
        self.created_subscriptions.clear()


class BigQueryHelper:
    """Helper class for managing BigQuery resources during tests."""
    
    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.created_tables = []
    
    def create_test_table(self, table_name: str, schema: List[bigquery.SchemaField]) -> str:
        """
        Create a test table.
        
        Args:
            table_name: Name of the table to create
            schema: BigQuery schema for the table
            
        Returns:
            Full table ID
        """
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.client.create_table(table)
            self.created_tables.append(table_id)
            logger.info(f"Created table: {table_id}")
        except Conflict:
            logger.info(f"Table already exists: {table_id}")
        
        return table_id
    
    def wait_for_data(self, table_id: str, expected_count: int, timeout: int = 300) -> bool:
        """
        Wait for data to appear in a table.
        
        Args:
            table_id: Full table ID
            expected_count: Expected number of rows
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if data appeared, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            query = f"SELECT COUNT(*) as count FROM `{table_id}`"
            result = list(self.client.query(query).result())
            
            if result and result[0].count >= expected_count:
                logger.info(f"Found {result[0].count} rows in {table_id}")
                return True
            
            time.sleep(10)  # Wait 10 seconds before checking again
        
        logger.warning(f"Timeout waiting for data in {table_id}")
        return False
    
    def get_table_data(self, table_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get data from a table.
        
        Args:
            table_id: Full table ID
            limit: Maximum number of rows to return
            
        Returns:
            List of row dictionaries
        """
        query = f"SELECT * FROM `{table_id}` LIMIT {limit}"
        result = self.client.query(query).result()
        
        rows = []
        for row in result:
            rows.append(dict(row.items()))
        
        return rows
    
    def validate_table_schema(self, table_id: str, expected_schema: Dict[str, str]) -> bool:
        """
        Validate table schema matches expected schema.
        
        Args:
            table_id: Full table ID
            expected_schema: Dictionary of field_name -> field_type
            
        Returns:
            True if schema matches, False otherwise
        """
        table = self.client.get_table(table_id)
        actual_schema = {field.name: field.field_type for field in table.schema}
        
        for field_name, field_type in expected_schema.items():
            if field_name not in actual_schema:
                logger.error(f"Missing field {field_name} in table {table_id}")
                return False
            
            if actual_schema[field_name].upper() != field_type.upper():
                logger.error(
                    f"Field {field_name} type mismatch in {table_id}: "
                    f"expected {field_type}, got {actual_schema[field_name]}"
                )
                return False
        
        return True
    
    def cleanup(self):
        """Clean up all created tables."""
        for table_id in self.created_tables:
            try:
                self.client.delete_table(table_id)
                logger.info(f"Deleted table: {table_id}")
            except NotFound:
                logger.warning(f"Table not found during cleanup: {table_id}")
        
        self.created_tables.clear()


class DataflowHelper:
    """Helper class for managing Dataflow jobs during tests."""
    
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        self.created_jobs = []
    
    def wait_for_job_completion(self, job_id: str, timeout: int = 600) -> bool:
        """
        Wait for a Dataflow job to complete.
        
        Args:
            job_id: Dataflow job ID
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if job completed successfully, False otherwise
        """
        import subprocess
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run([
                    "gcloud", "dataflow", "jobs", "describe", job_id,
                    "--region", self.region,
                    "--format", "value(currentState)"
                ], capture_output=True, text=True, check=True)
                
                state = result.stdout.strip()
                logger.info(f"Job {job_id} state: {state}")
                
                if state in ["JOB_STATE_DONE", "JOB_STATE_UPDATED"]:
                    return True
                elif state in ["JOB_STATE_FAILED", "JOB_STATE_CANCELLED"]:
                    logger.error(f"Job {job_id} failed with state: {state}")
                    return False
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Error checking job status: {e}")
                return False
            
            time.sleep(30)  # Check every 30 seconds
        
        logger.warning(f"Timeout waiting for job {job_id} to complete")
        return False
    
    def cleanup(self):
        """Clean up any running jobs."""
        # Note: In practice, you might want to cancel running test jobs
        # For now, we'll just log the jobs that were created
        for job_id in self.created_jobs:
            logger.info(f"Test job created: {job_id}")
        
        self.created_jobs.clear()


def generate_unique_resource_name(prefix: str, suffix_length: int = 8) -> str:
    """
    Generate a unique resource name for testing.
    
    Args:
        prefix: Prefix for the resource name
        suffix_length: Length of the random suffix
        
    Returns:
        Unique resource name
    """
    suffix = str(uuid.uuid4()).replace('-', '')[:suffix_length]
    return f"{prefix}-{suffix}"


def cleanup_all_test_resources(
    pubsub_helper: PubSubHelper,
    bigquery_helper: BigQueryHelper,
    dataflow_helper: DataflowHelper
):
    """
    Clean up all test resources.
    
    Args:
        pubsub_helper: PubSub helper instance
        bigquery_helper: BigQuery helper instance
        dataflow_helper: Dataflow helper instance
    """
    logger.info("Starting cleanup of all test resources...")
    
    try:
        pubsub_helper.cleanup()
    except Exception as e:
        logger.error(f"Error cleaning up Pub/Sub resources: {e}")
    
    try:
        bigquery_helper.cleanup()
    except Exception as e:
        logger.error(f"Error cleaning up BigQuery resources: {e}")
    
    try:
        dataflow_helper.cleanup()
    except Exception as e:
        logger.error(f"Error cleaning up Dataflow resources: {e}")
    
    logger.info("Cleanup completed")
