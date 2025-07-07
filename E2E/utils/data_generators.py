"""
Test data generators for CityPulse E2E test suite.

This module provides functions to generate various types of test data
for validating the data processing pipeline.
"""

import json
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker

fake = Faker()


def generate_citizen_report(
    event_id: Optional[str] = None,
    valid: bool = True,
    **overrides
) -> Dict[str, Any]:
    """
    Generate a citizen report event.
    
    Args:
        event_id: Optional event ID, generates random if None
        valid: Whether to generate valid or invalid data
        **overrides: Override specific fields
    
    Returns:
        Dictionary containing citizen report data
    """
    if not event_id:
        event_id = str(uuid.uuid4())
    
    # Base valid citizen report
    report = {
        "event_id": event_id,
        "title": fake.sentence(nb_words=6),
        "description": fake.text(max_nb_chars=200),
        "location": {
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude()),
            "address": fake.address()
        },
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": None,
        "category": random.choice([
            "Infrastructure", "Safety", "Environment", 
            "Transportation", "Public Services", "Other"
        ]),
        "severity": random.choice(["low", "medium", "high", "critical"]),
        "source": "citizen_app",
        "status": "open",
        "user_id": fake.uuid4(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "app_version": "1.0.0",
            "device_type": "mobile"
        }
    }
    
    # Add optional fields randomly
    if random.choice([True, False]):
        report["image_url"] = fake.image_url()
    
    if random.choice([True, False]):
        report["maps_url"] = f"https://maps.google.com/?q={report['location']['latitude']},{report['location']['longitude']}"
    
    # Apply overrides
    report.update(overrides)
    
    # Make invalid if requested
    if not valid:
        report = _make_invalid_citizen_report(report)
    
    return report


def generate_iot_data(
    device_id: Optional[str] = None,
    valid: bool = True,
    **overrides
) -> Dict[str, Any]:
    """
    Generate IoT sensor data.
    
    Args:
        device_id: Optional device ID, generates random if None
        valid: Whether to generate valid or invalid data
        **overrides: Override specific fields
    
    Returns:
        Dictionary containing IoT data
    """
    if not device_id:
        device_id = f"sensor_{fake.uuid4()[:8]}"
    
    sensor_types = [
        "air_quality", "noise_level", "traffic_flow", 
        "temperature", "humidity", "light_level"
    ]
    
    sensor_type = random.choice(sensor_types)
    
    # Generate realistic values based on sensor type
    value_ranges = {
        "air_quality": (0, 500),
        "noise_level": (30, 120),
        "traffic_flow": (0, 1000),
        "temperature": (-20, 50),
        "humidity": (0, 100),
        "light_level": (0, 100000)
    }
    
    units = {
        "air_quality": "AQI",
        "noise_level": "dB",
        "traffic_flow": "vehicles/hour",
        "temperature": "°C",
        "humidity": "%",
        "light_level": "lux"
    }
    
    min_val, max_val = value_ranges[sensor_type]
    
    data = {
        "device_id": device_id,
        "sensor_type": sensor_type,
        "measurement_value": round(random.uniform(min_val, max_val), 2),
        "measurement_unit": units[sensor_type],
        "location": {
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude())
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "quality_score": round(random.uniform(0.7, 1.0), 2),
        "metadata": {
            "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "battery_level": random.randint(10, 100)
        }
    }
    
    # Apply overrides
    data.update(overrides)
    
    # Make invalid if requested
    if not valid:
        data = _make_invalid_iot_data(data)
    
    return data


def generate_ai_processing_result(
    event_id: str,
    **overrides
) -> Dict[str, Any]:
    """
    Generate AI processing result data.
    
    Args:
        event_id: Event ID this result is for
        **overrides: Override specific fields
    
    Returns:
        Dictionary containing AI processing result
    """
    result = {
        "event_id": event_id,
        "ai_summary": fake.text(max_nb_chars=150),
        "ai_category": random.choice([
            "Infrastructure", "Safety", "Environment", 
            "Transportation", "Public Services"
        ]),
        "ai_image_tags": [
            fake.word() for _ in range(random.randint(2, 6))
        ],
        "ai_generated_image_url": fake.image_url(),
        "processing_timestamp": datetime.now(timezone.utc).isoformat(),
        "confidence_score": round(random.uniform(0.6, 0.95), 2),
        "processing_duration_ms": random.randint(500, 3000),
        "model_version": "v2.1.0"
    }
    
    # Apply overrides
    result.update(overrides)
    
    return result


def generate_batch_citizen_reports(
    count: int,
    valid_ratio: float = 0.8
) -> List[Dict[str, Any]]:
    """
    Generate a batch of citizen reports.
    
    Args:
        count: Number of reports to generate
        valid_ratio: Ratio of valid to invalid reports (0.0 to 1.0)
    
    Returns:
        List of citizen report dictionaries
    """
    reports = []
    valid_count = int(count * valid_ratio)
    
    for i in range(count):
        is_valid = i < valid_count
        report = generate_citizen_report(valid=is_valid)
        reports.append(report)
    
    return reports


def generate_batch_iot_data(
    count: int,
    valid_ratio: float = 0.9
) -> List[Dict[str, Any]]:
    """
    Generate a batch of IoT data points.
    
    Args:
        count: Number of data points to generate
        valid_ratio: Ratio of valid to invalid data (0.0 to 1.0)
    
    Returns:
        List of IoT data dictionaries
    """
    data_points = []
    valid_count = int(count * valid_ratio)
    
    for i in range(count):
        is_valid = i < valid_count
        data = generate_iot_data(valid=is_valid)
        data_points.append(data)
    
    return data_points


def _make_invalid_citizen_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Make a citizen report invalid for testing error handling."""
    invalid_types = [
        "missing_required_field",
        "wrong_data_type", 
        "invalid_enum_value",
        "malformed_location"
    ]
    
    invalid_type = random.choice(invalid_types)
    
    if invalid_type == "missing_required_field":
        # Remove a required field
        required_fields = ["event_id", "title", "description", "category"]
        field_to_remove = random.choice(required_fields)
        if field_to_remove in report:
            del report[field_to_remove]
    
    elif invalid_type == "wrong_data_type":
        # Change data type of a field
        report["start_time"] = "not_a_timestamp"
        
    elif invalid_type == "invalid_enum_value":
        # Use invalid enum value
        report["severity"] = "invalid_severity"
        
    elif invalid_type == "malformed_location":
        # Malform location data
        report["location"] = "not_an_object"
    
    return report


def _make_invalid_iot_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Make IoT data invalid for testing error handling."""
    invalid_types = [
        "missing_device_id",
        "negative_quality_score",
        "invalid_measurement_value",
        "malformed_timestamp"
    ]
    
    invalid_type = random.choice(invalid_types)
    
    if invalid_type == "missing_device_id":
        del data["device_id"]
    elif invalid_type == "negative_quality_score":
        data["quality_score"] = -0.5
    elif invalid_type == "invalid_measurement_value":
        data["measurement_value"] = "not_a_number"
    elif invalid_type == "malformed_timestamp":
        data["timestamp"] = "invalid_timestamp"
    
    return data


def save_sample_data_to_file(filename: str, count: int = 20):
    """
    Save sample test data to a JSON file.
    
    Args:
        filename: Output filename
        count: Number of samples to generate
    """
    sample_data = {
        "citizen_reports": {
            "valid": generate_batch_citizen_reports(count, valid_ratio=1.0),
            "invalid": generate_batch_citizen_reports(5, valid_ratio=0.0)
        },
        "iot_data": {
            "valid": generate_batch_iot_data(count, valid_ratio=1.0),
            "invalid": generate_batch_iot_data(5, valid_ratio=0.0)
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(sample_data, f, indent=2, default=str)
    
    print(f"Sample data saved to {filename}")


if __name__ == "__main__":
    # Generate sample data file
    save_sample_data_to_file("../data/sample_events.json")
