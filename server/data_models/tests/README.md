# Data Models Tests

This directory contains the test suite for the CityPulse data models, pipelines, and related
services. The tests are written using `pytest`and are designed to ensure the correctness and
reliability of the data layer.

## Testing Philosophy

Our testing strategy focuses on three main areas:

1.  **Unit Tests**: These tests verify the functionality of individual components, such as data
    models and utility functions, in isolation.

1.  **Integration Tests**: These tests ensure that different parts of the system work together as
    expected. For example, they test the interaction between the Firestore service and the data
    models.

1.  **Pipeline Tests**: These tests validate the logic of the data ingestion pipelines, ensuring
    that they can process data correctly.

## Running Tests

To run the tests, first make sure you have set up the development environment and installed the
required dependencies as described in the main`README.md`.

### Basic Test Execution

-     **Run all tests**:
  ````bash
  pytest
  ```-    **Run tests in a specific file**:```bash
  pytest data_models/tests/test_firestore_models.py
  ```-    **Run a specific test function**:```bash
  pytest data_models/tests/test_firestore_models.py::test_event_model_comprehensive
  ```### Test Coverage
  ````

We aim for high test coverage to ensure the quality of our code. To generate a coverage report,
run:```bash pytest --cov=data_models

````text

To view the report in HTML format, run:

```bash

pytest --cov=data_models --cov-report=html

```text

This will create an `htmlcov`directory. Open`htmlcov/index.html`in your browser to view the detailed report.

## Test Structure

The`tests`directory is organized as follows:

- `common.py`: Provides shared utilities and mock data for the tests.
-     `conftest.py`: Contains shared `pytest`fixtures used across multiple test files.
- `test_base_pipeline.py`: Includes base test classes for the data ingestion pipelines.
-     `test_bigquery_setup.py`: Contains tests for the BigQuery table setup script.
-     `test_citizen_report_pipeline.py`: Includes tests for the citizen report data pipeline.
-     `test_firestore_models.py`: Contains tests for the Firestore data models and repository.
-     `test_pipelines.py`: Provides tests for the main data pipeline classes.
-     `test_schema_validation.py`: Contains tests for the BigQuery schema validation script.

## Mocking

To isolate the tests from external services, we use mocking extensively. The `unittest.mock`library is used to mock
objects suchs as the Firestore client and BigQuery client. This allows us to test the application's logic without making
actual calls to these services.

Fixtures for mock objects are defined in`conftest.py` and can be injected into test functions as needed.
````
