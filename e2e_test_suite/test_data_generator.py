"""
A production-grade Python script for generating and publishing mock data to a
Google Cloud Pub/Sub topic for end-to-end testing of data pipelines.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Tuple

from google.cloud import pubsub_v1

def generate_and_publish_mock_data(project_id: str, topic_name: str) -> None:
    """
    Generates a diverse set of mock JSON messages and publishes them to a Pub/Sub topic.

    This function is designed to generate test data that covers various scenarios
    for the associated Beam pipeline, including valid records, records with
    missing fields, records with incorrect data types, and malformed JSON.

    Args:
        project_id: The Google Cloud project ID.
        topic_name: The name of the Pub/Sub topic to publish to.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    test_messages: List[Tuple[str, str]] = [
        # 1. Valid Records: Conform to the expected schema.
        (
            json.dumps({
                "event_id": str(uuid.uuid4()),
                "user_id": 1001,
                "event_timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            }),
            "Valid record 1"
        ),
        (
            json.dumps({
                "event_id": str(uuid.uuid4()),
                "user_id": 1002,
                "event_timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            }),
            "Valid record 2"
        ),
        # 2. Records with Null/Missing Fields: 'user_id' is missing.
        (
            json.dumps({
                "event_id": str(uuid.uuid4()),
                "event_timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            }),
            "Record with missing user_id"
        ),
        # 3. Records with Incorrect Data Types: 'user_id' is a string.
        (
            json.dumps({
                "event_id": str(uuid.uuid4()),
                "user_id": "user-1003",  # Should be an integer
                "event_timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            }),
            "Record with incorrect user_id type"
        ),
        # 4. Malformed JSON: A string that is not valid JSON.
        (
            "this is not json",
            "Malformed JSON string"
        )
    ]

    print(f"Publishing messages to {topic_path}...")
    for message_data, description in test_messages:
        try:
            # Pub/Sub messages must be bytestrings.
            future = publisher.publish(topic_path, data=message_data.encode("utf-8"))
            # Get the message ID from the future.
            message_id = future.result()
            print(f"Published message with ID: {message_id} ({description})")
        except Exception as e:
            print(f"Failed to publish message ({description}): {e}")

    print("Finished publishing all test messages.")