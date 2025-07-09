#!/usr/bin/env python3
"""
Publish test messages directly to the main citizen reports topic.
"""

import json
import logging
from datetime import datetime, timezone

from google.cloud import pubsub_v1
from utils.data_generators import generate_citizen_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_test_messages():
    """Publish test messages to the main citizen reports topic."""
    project_id = "citypulse-21"
    topic_name = "citypulse-citizen_reports"  # Main topic, not ingestion
    
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    
    logger.info(f"Publishing to topic: {topic_path}")
    
    # Generate and publish 3 test messages
    for i in range(3):
        # Generate test data
        test_data = generate_citizen_report(valid=True)
        
        # Convert to JSON
        message_data = json.dumps(test_data, default=str).encode('utf-8')
        
        # Publish message
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()
        
        logger.info(f"Published message {i+1}: {message_id} - Event ID: {test_data['event_id']}")
    
    logger.info("✅ All test messages published successfully!")

if __name__ == "__main__":
    publish_test_messages()
