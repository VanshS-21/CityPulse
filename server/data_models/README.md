# CityPulse Data Models

This directory contains the core data models, schemas, and data processing pipelines for the CityPulse application. It defines the data structures for real-time access in Firestore and for long-term analytics in BigQuery.

## Getting Started

To get started with the data models and pipelines, follow these steps:

1.  **Set up the Environment**: The data ingestion pipelines are built with Apache Beam and require a specific Python environment. These pipelines are tested and confirmed to work with **Python 3.11**.

    *   **Create a Virtual Environment**:
        ```bash
        # From the project root directory (f:/CityPulse)
        py -3.11 -m venv .venv
        ```

    *   **Activate the Environment**:
        ```bash
        # On Windows
        .\.venv\Scripts\activate
        ```

    *   **Install Dependencies**:
        ```bash
        pip install -r requirements.txt
        ```

2.  **Configure the Project**: All configurations for GCP, BigQuery, and Pub/Sub are centralized in `data_models/core/config.py`. You will need to update this file with your project-specific settings.

3.  **Run Tests**: To ensure everything is set up correctly, run the tests using `pytest`:
    ```bash
    pytest
    ```

## Project Structure

The `data_models` directory is organized as follows:

-   `data_ingestion/`: Includes the Apache Beam pipelines for processing real-time data from various sources.
-   `firestore_models/`: Defines the Python classes that map to Firestore documents (now using shared models).
-   `schemas/`: Contains the JSON schemas for the BigQuery tables.
-   `services/`: Provides a high-level service for interacting with Firestore.
-   `tests/`: Contains unit and integration tests for the data models and pipelines.
-   `transforms/`: Includes reusable transformations for the data pipelines.
-   `utils/`: Provides utility functions and classes used across the project.

**Note**: Configuration has been moved to the unified `shared_config.py` at the project root for consistency across all CityPulse components.

---

## Firestore Models

The Firestore models are Python classes that provide a structured way to work with Firestore documents. They include data validation, business logic, and helper methods for data manipulation.

### Core Models

-   **`BaseModel`**: An abstract base class that provides common fields like `id`, `created_at`, and `updated_at`.
-   **`Event`**: Represents city-related events, such as traffic incidents or public announcements.
-   **`UserProfile`**: Stores user-specific data, including preferences and roles.
-   **`Feedback`**: Manages user-submitted feedback and suggestions.

### Firestore Service

The `services/firestore_service.py` module offers a simplified interface for performing CRUD operations on Firestore. It uses a generic `FirestoreRepository` that can work with any `BaseModel` subclass, promoting code reuse and simplifying data access.

---

## BigQuery Schemas

The `schemas/` directory contains JSON files that define the structure of the BigQuery tables used for data analytics. These schemas include configurations for table partitioning and clustering to optimize query performance.

### Schema Validation

A validation script, `validate_schemas.py`, is provided to ensure that the schemas are correctly formatted before deployment.

```bash
python validate_schemas.py
```text
### Table Setup

The `setup_bigquery_tables.py` script creates the BigQuery dataset and tables based on the JSON schemas.

```bash
python setup_bigquery_tables.py --project-id YOUR_PROJECT_ID
```text
---

## Data Ingestion Pipelines

The data ingestion pipelines are built using Apache Beam and are designed to run on Google Cloud Dataflow. They process streaming data from Pub/Sub and load it into BigQuery for analysis.

### Running the Pipelines

The pipelines can be run locally for development and testing. They are streaming pipelines and will continue to run until manually stopped.

-   **Citizen Report Pipeline**:
    ```bash
    python -m data_models.data_ingestion.citizen_report_pipeline
    ```

-   **Social Media Pipeline**:
    ```bash
    python -m data_models.data_ingestion.social_media_pipeline
    ```

-   **Official Feeds Pipeline**:
    ```bash
    python -m data_models.data_ingestion.official_feeds_pipeline
    ```

### Configuration

All pipeline settings, including GCP project ID, Pub/Sub topics, and BigQuery table names, are now managed through the unified configuration system in `shared_config.py`. This provides centralized configuration management across the entire CityPulse platform.

---

## Deployment

The data models and pipelines are designed to be deployed to a Google Cloud environment. The infrastructure required to run the pipelines can be provisioned using the Terraform scripts in the `infra/` directory.

Once the infrastructure is in place, the Dataflow pipelines can be deployed using a CI/CD pipeline or manually through the gcloud CLI.

---

## Testing

The `tests/` directory contains a suite of tests for the data models, schemas, and pipelines. To run the tests, use `pytest`:

```bash
pytest
```text
