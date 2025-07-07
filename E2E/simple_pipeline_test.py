#!/usr/bin/env python3
"""
Simple pipeline test to verify E2E data flow without complex Apache Beam setup.
This script pulls messages from Pub/Sub and writes them directly to BigQuery.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

from google.cloud import pubsub_v1, bigquery
from google.api_core import exceptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplePipelineTest:
    """Simple pipeline to test E2E data flow."""
    
    def __init__(self, project_id: str, subscription_name: str, table_id: str):
        self.project_id = project_id
        self.subscription_path = f"projects/{project_id}/subscriptions/{subscription_name}"
        self.table_id = table_id
        
        # Initialize clients
        self.subscriber = pubsub_v1.SubscriberClient()
        self.bigquery_client = bigquery.Client(project=project_id)
        
        logger.info(f"Initialized pipeline test for {subscription_name} -> {table_id}")
    
    def process_message(self, message) -> Dict[str, Any]:
        """Process a Pub/Sub message and convert it to BigQuery format."""
        try:
            # Parse the message data
            data = json.loads(message.data.decode('utf-8'))
            logger.info(f"Processing message: {data.get('event_id', 'unknown')}")
            
            # Convert location to GEOGRAPHY format if needed
            if 'location' in data and isinstance(data['location'], dict):
                lat = data['location'].get('latitude')
                lng = data['location'].get('longitude')
                if lat is not None and lng is not None:
                    data['location'] = f"POINT({lng} {lat})"
            
            # Ensure required timestamps
            if 'created_at' not in data:
                data['created_at'] = datetime.now(timezone.utc).isoformat()
            
            # Convert metadata to JSON string if it's a dict
            if 'metadata' in data and isinstance(data['metadata'], dict):
                data['metadata'] = json.dumps(data['metadata'])
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None
    
    def write_to_bigquery(self, rows: list):
        """Write processed rows to BigQuery."""
        if not rows:
            return
        
        try:
            table = self.bigquery_client.get_table(self.table_id)
            errors = self.bigquery_client.insert_rows_json(table, rows)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.info(f"Successfully inserted {len(rows)} rows to BigQuery")
                
        except Exception as e:
            logger.error(f"Error writing to BigQuery: {e}")
    
    def run(self, max_messages: int = 10, timeout: int = 60):
        """Run the simple pipeline test."""
        logger.info(f"Starting pipeline test - max_messages: {max_messages}, timeout: {timeout}s")
        
        processed_rows = []
        messages_processed = 0
        start_time = time.time()
        
        def callback(message):
            nonlocal messages_processed, processed_rows
            
            if messages_processed >= max_messages:
                return
            
            # Process the message
            row = self.process_message(message)
            if row:
                processed_rows.append(row)
                messages_processed += 1
                logger.info(f"Processed message {messages_processed}/{max_messages}")
            
            # Acknowledge the message
            message.ack()
        
        # Start pulling messages
        flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, 
            callback=callback,
            flow_control=flow_control
        )
        
        logger.info(f"Listening for messages on {self.subscription_path}...")
        
        try:
            # Wait for messages or timeout
            while time.time() - start_time < timeout and messages_processed < max_messages:
                time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            streaming_pull_future.cancel()
            streaming_pull_future.result()  # Block until the shutdown is complete
        
        # Write collected rows to BigQuery
        if processed_rows:
            self.write_to_bigquery(processed_rows)
            logger.info(f"Pipeline test completed - processed {len(processed_rows)} messages")
        else:
            logger.warning("No messages were processed")
        
        return len(processed_rows)


if __name__ == "__main__":
    # Configuration
    PROJECT_ID = "citypulse-21"
    SUBSCRIPTION_NAME = "citypulse-citizen_reports-subscription"  # We need to create this
    TABLE_ID = "citypulse-21.citypulse_analytics.events"
    
    # Create and run the test
    pipeline_test = SimplePipelineTest(PROJECT_ID, SUBSCRIPTION_NAME, TABLE_ID)
    pipeline_test.run(max_messages=5, timeout=30)
