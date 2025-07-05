"""Tests for schema validation functionality."""
import json

import pytest

from data_models import validate_schemas

# Sample valid schema for testing
VALID_SCHEMA = {
    "name": "TestSchema",
    "description": "Test schema for validation",
    "fields": [{
        "name": "id",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "Unique identifier"
    }, {
        "name": "count",
        "type": "INTEGER",
        "description": "A count value"
    }, {
        "name": "nested",
        "type": "RECORD",
        "fields": [{
            "name": "nested_field",
            "type": "STRING"
        }]
    }]
}

# Test cases for schema validation
SCHEMA_TEST_CASES = [(
    {
        "name": "Test",
        "description": "Test",
        "fields": [{
            "name": "id",
            "type": "STRING"
        }]
    }, True, "Valid minimal schema"),
                     ({
                         "description": "Test",
                         "fields": []
                     }, False, "Missing required key 'name'"),
                     ({
                         "name": "Test",
                         "fields": []
                     }, False, "Missing required key 'description'"),
                     ({
                         "name": "Test",
                         "description": "Test"
                     }, False, "Missing required key 'fields'"),
                     ({
                         "name": "Test",
                         "description": "Test",
                         "fields": [{
                             "type": "STRING"
                         }]
                     }, False, "Field missing 'name'"),
                     ({
                         "name": "Test",
                         "description": "Test",
                         "fields": [{
                             "name": "id"
                         }]
                     }, False, "Field missing 'type'"),
                     ({
                         "name": "Test",
                         "description": "Test",
                         "fields": [{
                             "name": "id",
                             "type": "INVALID"
                         }]
                     }, False, "Invalid field type"),
                     ({
                         "name": "Test",
                         "description": "Test",
                         "fields": [{
                             "name": "id",
                             "type": "STRING",
                             "mode": "INVALID"
                         }]
                     }, False, "Invalid field mode"),
                     ({
                         "name": "Test",
                         "description": "Test",
                         "fields": [{
                             "name": "id",
                             "type": "RECORD"
                         }]
                     }, False, "RECORD type missing fields")]


@pytest.fixture
def temp_schema_file(tmp_path):
    """Create a temporary schema file for testing."""
    schema_file = tmp_path / "valid_schema.json"
    schema_file.write_text(json.dumps(VALID_SCHEMA))
    return str(schema_file)


def test_validate_valid_schema(temp_schema_file):  # pylint: disable=redefined-outer-name
    """Test validation of a valid schema file."""
    validator = validate_schemas.SchemaValidator(temp_schema_file)
    is_valid, errors = validator.validate()
    assert is_valid is True, f"Validation failed unexpectedly: {errors}"
    assert not errors


def test_validate_invalid_json(tmp_path):
    """Test validation of invalid JSON file."""
    invalid_json_path = tmp_path / "invalid.json"
    invalid_json_path.write_text("{invalid json")
    validator = validate_schemas.SchemaValidator(str(invalid_json_path))
    is_valid, errors = validator.validate()
    assert is_valid is False
    assert any("Invalid JSON" in e for e in errors)


def test_validate_missing_file():
    """Test validation of non-existent file."""
    validator = validate_schemas.SchemaValidator("nonexistent.json")
    is_valid, errors = validator.validate()
    assert is_valid is False
    assert errors and "Schema file not found" in errors[0]


@pytest.mark.parametrize("schema,expected_valid,test_name", SCHEMA_TEST_CASES)
def test_schema_validation_cases(tmp_path, schema, expected_valid, test_name):
    """Test various schema validation scenarios."""
    test_file = tmp_path / "test_schema.json"
    test_file.write_text(json.dumps(schema))
    validator = validate_schemas.SchemaValidator(str(test_file))
    is_valid, errors = validator.validate()
    assert is_valid == expected_valid, f"Test '{test_name}' failed: {errors}"


def test_validate_nested_fields(tmp_path):
    """Test validation of nested fields."""
    schema = {
        "name": "NestedTest",
        "description": "Test nested fields",
        "fields": [{
            "name": "nested",
            "type": "RECORD",
            "fields": [
                {
                    "name": "valid",
                    "type": "STRING"
                },
                {
                    "type": "MISSING_NAME"
                }  # Invalid: missing name
            ]
        }]
    }
    test_file = tmp_path / "test_nested.json"
    test_file.write_text(json.dumps(schema))
    validator = validate_schemas.SchemaValidator(str(test_file))
    is_valid, errors = validator.validate()
    assert is_valid is False
    assert any("missing 'name' or 'type'" in e for e in errors)
