"""
BigQuery table tests for CityPulse E2E test suite.

This module tests BigQuery table schemas, data validation,
partitioning, and query performance.
"""

import pytest
from typing import List, Dict, Any
from google.cloud import bigquery

from ..config.test_config import get_all_configs, CITIZEN_REPORT_SCHEMA, IOT_DATA_SCHEMA, DEAD_LETTER_SCHEMA
from ..utils.gcp_helpers import BigQueryHelper, generate_unique_resource_name
from ..utils.data_generators import generate_citizen_report, generate_iot_data
from ..utils.test_helpers import TestTimer, validate_json_schema


@pytest.fixture(scope="module")
def configs():
    """Get test configurations."""
    return get_all_configs()


@pytest.fixture(scope="module") 
def bigquery_helper(configs):
    """Create BigQuery helper instance."""
    helper = BigQueryHelper(
        configs["gcp"].project_id,
        configs["bigquery"].dataset_id
    )
    yield helper
    helper.cleanup()


class TestBigQuerySchemas:
    """Test BigQuery table schema validation."""
    
    def test_events_table_schema(self, bigquery_helper, configs):
        """Test the main events table schema."""
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
        
        # Expected schema for events table - Updated to match actual production schema
        expected_schema = {
            "event_id": "STRING",
            "title": "STRING",
            "description": "STRING",
            "location": "GEOGRAPHY",  # Updated to match actual table
            "start_time": "TIMESTAMP",
            "end_time": "TIMESTAMP",
            "category": "STRING",
            "severity": "STRING",
            "source": "STRING",
            "status": "STRING",
            "user_id": "STRING",
            "created_at": "TIMESTAMP",
            "updated_at": "TIMESTAMP",
            "metadata": "JSON",
            "ai_summary": "STRING",
            "ai_category": "STRING",
            "ai_image_tags": "STRING",  # REPEATED fields show as STRING in schema
            "ai_generated_image_url": "STRING",
            "image_url": "STRING",
            "maps_url": "STRING"
        }
        
        schema_valid = bigquery_helper.validate_table_schema(table_id, expected_schema)
        assert schema_valid, f"Events table schema validation failed"
    
    def test_citizen_reports_table_schema(self, bigquery_helper, configs):
        """Test the citizen reports table schema."""
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].citizen_reports_table}"
        
        # Check if table exists, if not skip test
        try:
            bigquery_helper.client.get_table(table_id)
        except Exception:
            pytest.skip(f"Table {table_id} does not exist")
        
        expected_schema = {
            "event_id": "STRING",
            "title": "STRING",
            "description": "STRING", 
            "location": "JSON",
            "category": "STRING",
            "severity": "STRING",
            "status": "STRING",
            "user_id": "STRING",
            "created_at": "TIMESTAMP",
            "updated_at": "TIMESTAMP"
        }
        
        schema_valid = bigquery_helper.validate_table_schema(table_id, expected_schema)
        assert schema_valid, f"Citizen reports table schema validation failed"
    
    def test_dead_letter_table_schema(self, bigquery_helper, configs):
        """Test the dead letter events table schema."""
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].dead_letter_events_table}"
        
        # Updated to match actual dead letter table schema
        expected_schema = {
            "timestamp": "TIMESTAMP",
            "pipeline_step": "STRING",
            "raw_data": "STRING",
            "error_message": "STRING"
        }
        
        schema_valid = bigquery_helper.validate_table_schema(table_id, expected_schema)
        assert schema_valid, f"Dead letter table schema validation failed"


class TestBigQueryDataValidation:
    """Test data validation in BigQuery tables."""
    
    def test_insert_valid_citizen_report(self, bigquery_helper, configs):
        """Test inserting valid citizen report data."""
        # Create test table
        test_table_name = generate_unique_resource_name("test_citizen_reports")
        
        schema = [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING"),
            bigquery.SchemaField("location", "GEOGRAPHY"),  # Updated to match production schema
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("severity", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
        ]
        
        table_id = bigquery_helper.create_test_table(test_table_name, schema)
        
        # Generate test data
        test_data = generate_citizen_report(valid=True)
        
        # Insert data - Convert location to GEOGRAPHY format
        location_wkt = f"POINT({test_data['location']['longitude']} {test_data['location']['latitude']})"
        rows_to_insert = [{
            "event_id": test_data["event_id"],
            "title": test_data["title"],
            "description": test_data["description"],
            "location": location_wkt,  # Convert to Well-Known Text format for GEOGRAPHY
            "category": test_data["category"],
            "severity": test_data["severity"],
            "created_at": test_data["created_at"]
        }]
        
        errors = bigquery_helper.client.insert_rows_json(
            bigquery_helper.client.get_table(table_id), 
            rows_to_insert
        )
        
        assert len(errors) == 0, f"Failed to insert data: {errors}"
        
        # Verify data was inserted
        data_available = bigquery_helper.wait_for_data(table_id, 1, timeout=60)
        assert data_available, "Data was not inserted successfully"
        
        # Retrieve and validate data
        retrieved_data = bigquery_helper.get_table_data(table_id, limit=1)
        assert len(retrieved_data) == 1
        assert retrieved_data[0]["event_id"] == test_data["event_id"]
    
    def test_query_performance(self, bigquery_helper, configs):
        """Test query performance on main tables."""
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
        
        # Simple count query
        with TestTimer("count query") as timer:
            query = f"SELECT COUNT(*) as total FROM `{table_id}`"
            result = list(bigquery_helper.client.query(query).result())
        
        assert timer.duration < 30  # Should complete within 30 seconds
        assert len(result) == 1
        
        # Date range query
        with TestTimer("date range query") as timer:
            query = f"""
            SELECT COUNT(*) as total 
            FROM `{table_id}` 
            WHERE DATE(created_at) = CURRENT_DATE()
            """
            result = list(bigquery_helper.client.query(query).result())
        
        assert timer.duration < 30  # Should complete within 30 seconds
        assert len(result) == 1


class TestBigQueryDataIntegrity:
    """Test data integrity and constraints."""
    
    def test_current_production_data(self, bigquery_helper, configs):
        """Test current production data integrity."""
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
        
        # Check for required fields
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(event_id) as non_null_event_ids,
            COUNT(created_at) as non_null_created_at
        FROM `{table_id}`
        """
        
        result = list(bigquery_helper.client.query(query).result())
        row = result[0]
        
        # All rows should have event_id and created_at
        assert row.total_rows == row.non_null_event_ids, "Some rows missing event_id"
        assert row.total_rows == row.non_null_created_at, "Some rows missing created_at"
    
    def test_dead_letter_data_structure(self, bigquery_helper, configs):
        """Test dead letter table data structure."""
        table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].dead_letter_events_table}"
        
        # Get sample data from dead letter table
        sample_data = bigquery_helper.get_table_data(table_id, limit=5)
        
        for row in sample_data:
            # Verify required fields exist (updated to match actual schema)
            assert "timestamp" in row, "Dead letter row missing timestamp"
            assert "pipeline_step" in row, "Dead letter row missing pipeline_step"
            assert "raw_data" in row, "Dead letter row missing raw_data"
            assert "error_message" in row, "Dead letter row missing error_message"

            # Verify error_message field contains meaningful error info
            assert len(row["error_message"]) > 0, "Dead letter error_message is empty"
