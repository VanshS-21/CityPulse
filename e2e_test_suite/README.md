# E2E Test Suite

## Overview

This directory contains the end-to-end (E2E) test suite for the data processing pipeline. The purpose of this suite is to simulate the entire workflow, from data generation to pipeline execution and verification, ensuring that all components work together as expected in a production-like environment.

## Project Structure

```
e2e_test_suite/
├── beam_pipeline.py
├── conftest.py
├── e2e_pipeline_test.py
├── requirements.txt
└── test_data_generator.py
```

## Prerequisites

Before running the tests, ensure you have the following tools installed on your machine:

*   Python 3.8+
*   `gcloud` CLI

You also need to be authenticated with Google Cloud. Run the following command to log in:

```bash
gcloud auth application-default login
```

## Environment Setup

1.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set environment variables:**

    The following environment variables must be set before running the tests. You can export them in your shell or use a `.env` file.

    ```bash
    export GCP_PROJECT_ID="your-gcp-project-id"
    export GCP_REGION="your-gcp-region"
    export TEMP_GCS_BUCKET="your-gcs-bucket-for-temp-files"
    ```

## Execution

To run the entire E2E test suite, execute the following command from within the `e2e_test_suite` directory:

```bash
pytest -v