# CityPulse Data Models

This directory contains the core data models and schemas for the CityPulse application, defining the structure of data for both real-time access in Firestore and long-term storage in BigQuery.

## Overview

The data modeling approach separates real-time operational data from analytical data:

- **Firestore Models**: Python classes located in `firestore_models/` are used for real-time application features. They include business logic, helper methods, and use `Enums` for type safety.
- **BigQuery Schemas**: JSON files in `schemas/` define the table structure for data warehousing and analytics.

---

## Firestore Python Models

These models are designed for interacting with Firestore and are the primary way the application backend handles data.

### Core Models

- **`BaseModel`**: A base class providing common functionality like `id`, `created_at`, `updated_at`, and `to_dict()` / `from_dict()` methods.

- **`Event`**: Represents city events (e.g., traffic, public safety). Uses enums like `EventCategory`, `EventSeverity`, and `EventStatus`.

- **`UserProfile`**: Stores user-specific information, including preferences and roles (`UserRole` enum).

- **`Feedback`**: Manages user-submitted feedback, categorized by `FeedbackType` and `FeedbackStatus` enums.

### Example Usage

Here is how you might create an `Event` instance:

```python
from datetime import datetime
from data_models.firestore_models.event import Event, EventCategory, EventSeverity, EventSource

# Create a new event
event = Event(
    title="Road Closure on Main St",
    description="Emergency water main repair.",
    location={"latitude": 34.0522, "longitude": -118.2437},
    start_time=datetime.utcnow(),
    category=EventCategory.INFRASTRUCTURE,
    severity=EventSeverity.HIGH,
    source=EventSource.CITY_OFFICIAL
)

# Convert to dictionary for Firestore
data_to_save = event.to_dict()
```

### Firestore Service

The `firestore_service.py` module provides a high-level interface for interacting with Firestore. It uses a generic `FirestoreRepository` class that handles all CRUD (Create, Read, Update, Delete) operations for any `BaseModel` subclass, making the service lean and highly reusable.

---

## BigQuery Schemas

The JSON schemas in the `schemas/` directory define the structure for tables in BigQuery, which are used for long-term storage and analytics. These schemas also include partitioning and clustering configurations to optimize query performance and costs.

- `event_schema.json`
- `feedback_schema.json`

### Schema Validation

To ensure the schemas are valid before deployment, you can use the `validate_schemas.py` script. This script checks for correct data types, modes, and field names.

```bash
python validate_schemas.py
```

### BigQuery Table Setup

To create the BigQuery dataset and tables from the schema files, run the setup script with your Google Cloud project ID:

```bash
python setup_bigquery_tables.py --project-id YOUR_PROJECT_ID
```

---

## Data Ingestion Pipelines

This project includes scalable, streaming data ingestion pipelines built with Apache Beam. They are designed to run on Google Cloud Dataflow and process data from Pub/Sub topics in real-time.

### Environment Setup

The pipelines require a specific Python environment to ensure all dependencies are compatible.

1.  **Create a Virtual Environment**: These pipelines are tested and confirmed to work with **Python 3.11**. Create a virtual environment using this version:
    ```bash
    # From the project root directory (f:/CityPulse)
    py -3.11 -m venv .venv
    ```

2.  **Activate the Environment**:
    ```bash
    # On Windows
    .\.venv\Scripts\activate
    ```

3.  **Install Dependencies**: Install all the necessary Python packages from the `data_models` directory.
    ```bash
    pip install -r requirements.txt
    ```

### Running the Pipelines

The pipelines are configured to use the settings in `data_models/config.py`. You can run them locally for testing. Note that they are streaming pipelines and will run until manually stopped (`Ctrl+C`).

-   **Run the Citizen Report Pipeline**:
    ```bash
    python -m data_models.data_ingestion.citizen_report_pipeline
    ```
    This pipeline accepts command-line arguments to override the default configuration. For example:
    ```bash
    python -m data_models.data_ingestion.citizen_report_pipeline --output_table your_project:your_dataset.your_table
    ```

-   **Run the Social Media Pipeline**:
    ```bash
    python -m data_models.data_ingestion.social_media_pipeline
    ```

-   **Run the Official Feeds Pipeline**:
    ```bash
    python -m data_models.data_ingestion.official_feeds_pipeline
    ```
    This pipeline also accepts the `--event_schema` argument to specify a custom schema:
    ```bash
    python -m data_models.data_ingestion.official_feeds_pipeline --event_schema /path/to/your/schema.json
    ```

### Configuration

All pipeline configurations (Project ID, Pub/Sub topics, etc.) are centralized in `data_models/config.py`. Modify this file to change settings across all pipelines.

---

## Testing

The `tests/` directory is structured to hold unit and integration tests for the data models. To run the tests, you would typically use a test runner like `pytest`.

```bash
# Example of running tests with pytest
pytest
```
