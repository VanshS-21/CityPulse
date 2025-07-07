#!/usr/bin/env python3
"""
Quick test event publisher for CityPulse E2E testing.

This script publishes a single test event to the production Pub/Sub topic
for quick validation of the pipeline.
"""

import json
import time
import sys
import os
from datetime import datetime, timezone
from google.cloud import pubsub_v1

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data_models.core.config import PROJECT_ID, PUBSUB_CITIZEN_REPORTS_TOPIC

# Sample event data to publish
# This event includes a description and an image URL to test all AI features.
sample_event = {
    "event_id": f"evt_test_{int(time.time())}",
    "title": "E2E Test Event - Pothole Report",
    "user_id": "user_test_123",
    "category": "Infrastructure",
    "description": "There is a large pothole on the corner of Main St and 1st Ave. It's been there for weeks and is getting dangerous for cyclists.",
    "location": {
        "latitude": 34.052235,
        "longitude": -118.243683,
        "address": "Main St & 1st Ave, Los Angeles, CA"
    },
    "image_url": "https://storage.googleapis.com/gcp-public-data-landsat/LC08/01/044/034/LC08_L1GT_044034_20130330_20170310_01_T1/LC08_L1GT_044034_20130330_20170310_01_T1_thumb_large.jpg",
    "start_time": datetime.now(timezone.utc).isoformat(),
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "e2e_test",
    "status": "open",
    "severity": "high",
    "metadata": {
        "test_type": "e2e_validation",
        "script_version": "2.0"
    }
}


def publish_message(project_id: str, topic_id: str, message_data: dict):
    """Publishes a single message to a Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # Data must be a bytestring
    data = json.dumps(message_data).encode("utf-8")

    try:
        future = publisher.publish(topic_path, data)
        message_id = future.result()
        print(f"✅ Message {message_id} published to {topic_path}")
        print(f"📝 Event ID: {message_data['event_id']}")
        print(f"📍 Title: {message_data['title']}")
        return message_id
    except Exception as e:
        print(f"❌ An error occurred while publishing message: {e}")
        return None


def main():
    """Main function to publish test event."""
    print("🚀 CityPulse E2E Test Event Publisher")
    print("=" * 50)
    print(f"📡 Publishing test event to topic '{PUBSUB_CITIZEN_REPORTS_TOPIC}' in project '{PROJECT_ID}'...")
    print()
    
    message_id = publish_message(PROJECT_ID, PUBSUB_CITIZEN_REPORTS_TOPIC, sample_event)
    
    if message_id:
        print()
        print("🎯 Next steps:")
        print("1. Wait 2-3 minutes for pipeline processing")
        print("2. Check BigQuery events table for the new record")
        print("3. Verify AI processing results")
        print()
        print("💡 To check the results:")
        print(f"   bq query --use_legacy_sql=false \"SELECT * FROM \\`{PROJECT_ID}.citypulse_analytics.events\\` WHERE event_id = '{sample_event['event_id']}'\"")
    else:
        print("❌ Failed to publish test event")
        sys.exit(1)


if __name__ == "__main__":
    main()
