import json
import time
import sys
import os
from datetime import datetime, timezone
from google.cloud import pubsub_v1

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_models.config import PROJECT_ID, TOPIC_ID

# Sample event data to publish
# This event includes a description and an image URL to test all AI features.
sample_event = {
    "event_id": f"evt_test_{int(time.time())}",
    "user_id": "user_test_123",
    "event_type": "Infrastructure",
    "description": "There is a large pothole on the corner of Main St and 1st Ave. It's been there for weeks and is getting dangerous for cyclists.",
    "location": {
        "latitude": 34.052235,
        "longitude": -118.243683
    },
    "image_url": "https://storage.googleapis.com/gcp-public-data-landsat/LC08/01/044/034/LC08_L1GT_044034_20130330_20170310_01_T1/LC08_L1GT_044034_20130330_20170310_01_T1_thumb_large.jpg",
            "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "open",
    "severity": "high"
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
        print(f"Message {message_id} published to {topic_path}.")
        return message_id
    except Exception as e:
        print(f"An error occurred while publishing message: {e}")
        return None

if __name__ == "__main__":
    print(f"Publishing test event to topic '{TOPIC_ID}' in project '{PROJECT_ID}'...")
    publish_message(PROJECT_ID, TOPIC_ID, sample_event)
