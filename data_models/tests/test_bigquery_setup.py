"""Tests for BigQuery table setup functionality."""
import json
from unittest.mock import MagicMock

import pytest
from google.api_core.exceptions import NotFound
from google.cloud.bigquery import SchemaField

from data_models import setup_bigquery_tables

# Sample schema for testing
SAMPLE_SCHEMA = {
    "name": "TestSchema",
    "description": "Test schema",
    "partitioning": {
        "type": "DAY",
        "field": "event_timestamp"
    },
    "clustering": {
        "fields": ["event_type"]
    },
    "fields": [
        {
            "name": "id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique ID"
        },
        {
            "name": "nested",
            "type": "RECORD",
            "fields": [
                {
                    "name": "nested_field",
                    "type": "STRING"
                }
            ]
        }
    ]
}

def test_parse_fields():
    """Test parsing of nested fields."""
    fields = SAMPLE_SCHEMA['fields']
    # pylint: disable=protected-access
    result = setup_bigquery_tables._parse_schema_fields(fields)
    assert len(result) == 2
    assert isinstance(result[0], SchemaField)
    assert result[0].name == "id"
    assert result[0].field_type == "STRING"
    assert result[0].mode == "REQUIRED"
    assert isinstance(result[1], SchemaField)
    assert result[1].name == "nested"
    assert result[1].field_type == "RECORD"
    assert len(result[1].fields) == 1
    assert result[1].fields[0].name == "nested_field"

def test_load_schema_and_config(tmp_path):
    """Test loading a schema and config from a file."""
    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text(json.dumps(SAMPLE_SCHEMA))
    schema, config = setup_bigquery_tables.load_schema_and_config(schema_file)
    assert len(schema) == 2
    assert schema[0].name == "id"
    assert config["partitioning"]["type"] == "DAY"
    assert config["clustering"]["fields"] == ["event_type"]

def test_load_schema_invalid_file():
    """Test loading a non-existent schema file."""
    with pytest.raises(FileNotFoundError):
        setup_bigquery_tables.load_schema_and_config("nonexistent.json")

def test_create_table(mock_bigquery_client, tmp_path):
    """Test creating a BigQuery table from a schema."""
    mock_bigquery_client.get_table.side_effect = NotFound("Table not found")
    mock_table = MagicMock()
    mock_table.project = "test-project"
    mock_table.dataset_id = "test_dataset"
    mock_table.table_id = "test_table"
    mock_bigquery_client.create_table.return_value = mock_table
    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text(json.dumps(SAMPLE_SCHEMA))
    table = setup_bigquery_tables.create_table(
        client=mock_bigquery_client,
        project_id="test-project",
        dataset_id="test_dataset",
        table_name="test_table",
        schema_file=str(schema_file)
    )
    mock_bigquery_client.create_table.assert_called_once()
    created_table_arg = mock_bigquery_client.create_table.call_args[0][0]
    assert len(created_table_arg.schema) == 2
    assert created_table_arg.time_partitioning.field == "event_timestamp"
    assert created_table_arg.clustering_fields == ["event_type"]
    assert table == mock_table

def test_create_table_already_exists(mock_bigquery_client, tmp_path):
    """Test handling of existing tables."""
    mock_bigquery_client.get_table.return_value = MagicMock()
    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text(json.dumps(SAMPLE_SCHEMA))
    result = setup_bigquery_tables.create_table(
        client=mock_bigquery_client,
        project_id="test-project",
        dataset_id="test_dataset",
        table_name="existing_table",
        schema_file=str(schema_file)
    )
    assert result == mock_bigquery_client.get_table.return_value
    mock_bigquery_client.get_table.assert_called_once_with(
        "test-project.test_dataset.existing_table"
    )
    mock_bigquery_client.create_table.assert_not_called()
