""" 
Publishes mock IoT data to a Pub/Sub topic.

This script simulates IoT devices sending data to the CityPulse platform.
It generates random event data and publishes it to a Google Cloud Pub/Sub
topic, which can then be processed by a Dataflow pipeline.

To run this script, you need to have Google Cloud authentication set up.
For example, you can use `gcloud auth application-default login`.

Example:
    python publish_mock_iot_data.py --project_id your-gcp-project-id --topic_id your-pubsub-topic
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime

from google.cloud import pubsub_v1

# Add the project root to the Python path to allow for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_models.firestore_models.event import (
    Event,
    EventCategory,
    EventSeverity,
    EventSource,
)

# --- Mock Data Generation ---

LOCATIONS = [
    {"latitude": 34.0522, "longitude": -118.2437},  # Downtown LA
    {"latitude": 34.0600, "longitude": -118.2920},  # Koreatown
    {"latitude": 34.1523, "longitude": -118.1653},  # Pasadena
    {"latitude": 33.9416, "longitude": -118.4085},  # LAX Area
    {"latitude": 34.1016, "longitude": -118.3441},  # Hollywood
]

def generate_traffic_data():
    """Generates a mock traffic event."""
    location = random.choice(LOCATIONS)
    return {
        "title": f"Heavy Traffic on {random.choice(['I-10', 'I-405', 'US-101'])}",
        "description": f"Incident involving {random.randint(2, 5)} vehicles.",
        "location": location,
        "category": EventCategory.TRAFFIC,
        "severity": random.choice([EventSeverity.MEDIUM, EventSeverity.HIGH]),
        "source": EventSource.SENSOR,
        "metadata": {
            "sensor_id": f"traffic-sensor-{random.randint(100, 999)}",
            "average_speed_mph": random.randint(5, 25),
            "vehicles_per_minute": random.randint(50, 150),
        },
    }

def generate_air_quality_data():
    """Generates mock air quality data."""
    location = random.choice(LOCATIONS)
    return {
        "title": "Air Quality Alert",
        "description": "Elevated PM2.5 levels detected.",
        "location": location,
        "category": EventCategory.WEATHER,
        "severity": random.choice([EventSeverity.LOW, EventSeverity.MEDIUM]),
        "source": EventSource.SENSOR,
        "metadata": {
            "sensor_id": f"air-quality-sensor-{random.randint(100, 999)}",
            "aqi": random.randint(50, 150),
            "pm2_5_ug_m3": round(random.uniform(12.1, 55.4), 2),
        },
    }

def generate_noise_level_data():
    """Generates mock noise level data."""
    location = random.choice(LOCATIONS)
    return {
        "title": "Noise Level Anomaly",
        "description": "Unusually high noise levels detected.",
        "location": location,
        "category": EventCategory.PUBLIC_SAFETY,
        "severity": EventSeverity.LOW,
        "source": EventSource.SENSOR,
        "metadata": {
            "sensor_id": f"noise-sensor-{random.randint(100, 999)}",
            "decibels": random.randint(80, 120),
        },
    }

DATA_GENERATORS = [
    generate_traffic_data,
    generate_air_quality_data,
    generate_noise_level_data,
]

# --- Publisher ---

def publish_message(project_id: str, topic_id: str, message: dict):
    """Publishes a single message to a Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # The pipeline expects a UTF-8 encoded JSON string from the Event model.
    event = Event(**message, start_time=datetime.utcnow())
    data_str = event.model_dump_json()
    data = data_str.encode("utf-8")

    try:
        future = publisher.publish(topic_path, data)
        print(f"Published message ID: {future.result()} to {topic_path}")
    except Exception as e:
        print(f"An error occurred while publishing: {e}")

def main(project_id: str, topic_id: str, interval_seconds: int):
    """Generates and publishes mock data at a specified interval."""
    print(
        f"Starting mock IoT data publisher for project '{project_id}' on "
        f"topic '{topic_id}'."
    )
    print(f"Publishing new data every {interval_seconds} seconds. Press Ctrl+C to stop.")

    while True:
        try:
            # Choose a random data generator and create a message
            generator = random.choice(DATA_GENERATORS)
            message_data = generator()

            # Publish the message
            publish_message(project_id, topic_id, message_data)

            # Wait for the next interval
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nPublisher stopped.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            time.sleep(interval_seconds)  # Wait before retrying

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish mock IoT data to Pub/Sub.")
    parser.add_argument(
        "--project_id", help="Your Google Cloud project ID.", required=True
    )
    parser.add_argument(
        "--topic_id",
        help="The Pub/Sub topic ID to publish to.",
        default="iot-data",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="The interval in seconds between messages.",
    )
    args = parser.parse_args()

    main(args.project_id, args.topic_id, args.interval)
