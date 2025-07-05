# Data Models Tests

This directory contains tests for the data models and related functionality.

## Running Tests

1. Install the test dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Run all tests:
   ```bash
   pytest -v
   ```

3. Run tests with coverage report:
   ```bash
   pytest --cov=../
   ```

4. Generate HTML coverage report:
   ```bash
   pytest --cov=../ --cov-report=html
   ```
   Then open `htmlcov/index.html` in a web browser.

## Test Structure

- `test_schema_validation.py`: Tests for schema validation logic
- `test_bigquery_setup.py`: Tests for BigQuery table creation and schema loading

## Writing New Tests

- Place new test files in this directory with the prefix `test_`
- Use descriptive test function names starting with `test_`
- Use fixtures for common setup/teardown code
- Mock external services and file I/O when possible

## Fixtures

- `temp_schema_file`: Creates a temporary schema file for testing
- `mock_bigquery_client`: Provides a mocked BigQuery client

## Test Coverage

We aim to maintain high test coverage for all critical functionality. The current coverage report can be generated using the commands above.
