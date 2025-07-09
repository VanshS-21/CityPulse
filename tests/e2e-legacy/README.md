# CityPulse E2E Test Suite

## Overview

This directory contains the comprehensive end-to-end (E2E) test suite for the CityPulse data processing pipeline. The suite validates the entire data flow from Pub/Sub ingestion through Dataflow processing to BigQuery storage, including AI processing and error handling.

## Architecture

The E2E test suite validates:

1. **Pub/Sub Integration** - Message publishing and subscription
2. **Dataflow Pipeline** - Actual cloud Dataflow job execution
3. **BigQuery Tables** - All tables, schemas, and data validation
4. **AI Processing** - AI-powered features and transformations
5. **Error Handling** - Dead letter queues and error scenarios
6. **End-to-End Flow** - Complete data journey validation

## Directory Structure

```
E2E/
├── tests/                          # Test modules
│   ├── test_pubsub_integration.py  # Pub/Sub publishing/consuming tests
│   ├── test_dataflow_pipeline.py   # Dataflow job execution tests
│   ├── test_bigquery_tables.py     # BigQuery table validation tests
│   ├── test_ai_processing.py       # AI processing feature tests
│   └── test_end_to_end.py          # Complete E2E workflow tests
├── utils/                          # Utility modules
│   ├── test_helpers.py             # Common test utilities
│   ├── data_generators.py          # Test data generation
│   └── gcp_helpers.py              # GCP resource management
├── config/                         # Configuration
│   └── test_config.py              # Test configuration settings
├── data/                           # Test data
│   └── sample_events.json          # Sample test events
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Prerequisites

1. **Python 3.11+** (required for Apache Beam compatibility)
2. **Google Cloud CLI** (`gcloud`)
3. **Authenticated GCP Account**

```bash
gcloud auth application-default login
```

## Environment Setup

1. **Create virtual environment:**
```bash
cd E2E
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export GCP_PROJECT_ID="citypulse-21"
export GCP_REGION="us-central1"
export GCP_TEMP_BUCKET="citypulse-dataflow-temp"
```

## Running Tests

### Individual Test Modules

```bash
# Test Pub/Sub integration
pytest tests/test_pubsub_integration.py -v

# Test Dataflow pipeline
pytest tests/test_dataflow_pipeline.py -v

# Test BigQuery tables
pytest tests/test_bigquery_tables.py -v

# Test AI processing
pytest tests/test_ai_processing.py -v

# Test complete E2E flow
pytest tests/test_end_to_end.py -v
```

### Full Test Suite

```bash
# Run all tests
pytest -v

# Run with detailed output
pytest -v -s

# Run specific test pattern
pytest -k "test_citizen_reports" -v
```

## Test Categories

### 1. Pub/Sub Integration Tests
- Message publishing to topics
- Subscription creation and management
- Message format validation
- Error message handling

### 2. Dataflow Pipeline Tests
- Pipeline deployment and execution
- Data transformation validation
- Windowing and batching
- Resource scaling and performance

### 3. BigQuery Table Tests
- Schema validation for all tables
- Data type verification
- Partitioning and clustering
- Query performance

### 4. AI Processing Tests
- Image analysis and tagging
- Text summarization
- Category classification
- Generated content validation

### 5. End-to-End Tests
- Complete data flow validation
- Multi-pipeline coordination
- Error recovery scenarios
- Performance benchmarks

## Test Data

The test suite uses various types of test data:

- **Valid Events** - Properly formatted citizen reports
- **Invalid Events** - Malformed data for error testing
- **Edge Cases** - Boundary conditions and special scenarios
- **Performance Data** - Large datasets for load testing

## Monitoring and Validation

Each test includes:

- **Resource Cleanup** - Automatic cleanup of test resources
- **Data Validation** - Comprehensive data integrity checks
- **Performance Metrics** - Execution time and resource usage
- **Error Reporting** - Detailed failure analysis

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   gcloud auth application-default login
   ```

2. **Permission Issues**
   - Ensure service account has required roles
   - Check IAM permissions for test resources

3. **Resource Conflicts**
   - Tests use unique identifiers to avoid conflicts
   - Manual cleanup may be needed if tests fail

### Debug Mode

Run tests with debug logging:
```bash
pytest -v -s --log-cli-level=DEBUG
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Include proper cleanup in teardown
3. Add comprehensive assertions
4. Document test purpose and expected behavior
5. Update this README if adding new test categories
