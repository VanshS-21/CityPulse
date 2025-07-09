#!/usr/bin/env python3
"""
Script to validate JSON schema files.
"""
import json
import os
import sys


# pylint: disable=too-few-public-methods
class SchemaValidator:
    """Validates BigQuery JSON schema files."""

    VALID_TYPES = {
        "STRING",
        "INTEGER",
        "FLOAT",
        "BOOLEAN",
        "TIMESTAMP",
        "DATE",
        "TIME",
        "DATETIME",
        "GEOGRAPHY",
        "NUMERIC",
        "BIGNUMERIC",
        "JSON",
        "RECORD",
    }
    VALID_MODES = {"NULLABLE", "REQUIRED", "REPEATED"}

    def __init__(self, schema_path):
        self.schema_path = schema_path
        self.errors = []

    def validate(self):
        """Validate the schema file."""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            self._validate_structure(schema)
            self._validate_fields(schema.get("fields", []))
        except FileNotFoundError:
            self.errors.append(f"Schema file not found at '{self.schema_path}'")
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
        except TypeError as e:
            self.errors.append(f"An unexpected error occurred during validation: {e}")

        return not self.errors, self.errors

    def _validate_structure(self, schema):
        """Validate the basic structure of the schema."""
        required_keys = {"name", "description", "fields"}
        missing_keys = required_keys - set(schema.keys())
        if missing_keys:
            self.errors.append(
                f"Missing required top-level keys: {', '.join(missing_keys)}"
            )

    def _validate_fields(self, fields, parent_field="schema"):
        """Recursively validate a list of fields."""
        if not isinstance(fields, list):
            self.errors.append(f"'{parent_field}' fields must be a list.")
            return

        for i, field in enumerate(fields):
            field_name = field.get("name", f"field at index {i}")
            context = f"{parent_field}.{field_name}"

            if not all(k in field for k in ["name", "type"]):
                self.errors.append(
                    f"Field at index {i} in {parent_field} is missing 'name' or 'type'."
                )
                continue

            if field["type"] not in self.VALID_TYPES:
                self.errors.append(f"Invalid type '{field['type']}' in {context}.")

            if field.get("mode") and field["mode"] not in self.VALID_MODES:
                self.errors.append(f"Invalid mode '{field['mode']}' in {context}.")

            if field["type"] == "RECORD":
                if "fields" not in field or not isinstance(field.get("fields"), list):
                    self.errors.append(
                        f"RECORD field '{context}' must have a 'fields' list."
                    )
                else:
                    self._validate_fields(field["fields"], parent_field=context)


def validate_schema(schema_path):
    """Validates a single schema file using the SchemaValidator class.

    This is a helper function for testing purposes.
    """
    validator = SchemaValidator(schema_path)
    is_valid, errors = validator.validate()
    return is_valid, errors


def main():
    """Validates all schema files in the 'schemas' directory."""
    schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
    if not os.path.isdir(schemas_dir):
        print(f"Error: Schemas directory not found at '{schemas_dir}'.")
        sys.exit(1)

    schema_files = [f for f in os.listdir(schemas_dir) if f.endswith(".json")]
    if not schema_files:
        print("No schema files found to validate.")
        sys.exit(0)

    print(f"Validating {len(schema_files)} schema files...\n")
    all_valid = True
    for schema_file in schema_files:
        validator = SchemaValidator(os.path.join(schemas_dir, schema_file))
        is_valid, errors = validator.validate()
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"- {schema_file}: {status}")
        if not is_valid:
            all_valid = False
            for error in errors:
                print(f"  - {error}")

    print("\nValidation finished.")
    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
