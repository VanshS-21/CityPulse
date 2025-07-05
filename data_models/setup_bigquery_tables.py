#!/usr/bin/env python3
"""
Script to set up BigQuery tables for CityPulse based on JSON schema definitions.
"""
import os
import json
import argparse
from google.cloud import bigquery, exceptions
from google.oauth2 import service_account

def load_schema_and_config(schema_file):
    """Load schema and table config from a JSON file."""
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_def = json.load(f)

    schema = _parse_schema_fields(schema_def.get('fields', []))
    config = {
        "partitioning": schema_def.get("partitioning"),
        "clustering": schema_def.get("clustering")
    }
    return schema, config

def _parse_schema_fields(fields):
    """Recursively parse schema fields from a list of dictionaries."""
    if not fields:
        return []

    return [
        bigquery.SchemaField(
            name=field['name'],
            field_type=field['type'],
            mode=field.get('mode', 'NULLABLE'),
            description=field.get('description', ''),
            fields=_parse_schema_fields(field.get('fields', []))
        )
        for field in fields
    ]

def create_table(client, project_id, dataset_id, table_name, schema_file):
    """
    Create a BigQuery table from a schema file, including partitioning and clustering.

    If the table already exists, it will not be modified.
    """
    table_id = f"{project_id}.{dataset_id}.{table_name}"

    try:
        table = client.get_table(table_id)
        print(f"Table {table_id} already exists. Skipping creation.")
    except exceptions.NotFound:
        print(f"Table {table_id} not found. Creating...")
        schema, config = load_schema_and_config(schema_file)
        table = bigquery.Table(table_id, schema=schema)

        if config.get("partitioning"):
            part_conf = config["partitioning"]
            table.time_partitioning = bigquery.TimePartitioning(
                type_=getattr(bigquery.TimePartitioningType, part_conf["type"]),
                field=part_conf["field"]
            )

        if config.get("clustering"):
            table.clustering_fields = config["clustering"]["fields"]

        table = client.create_table(table)
        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

    return table

def main():
    """Main function to set up BigQuery tables."""
    parser = argparse.ArgumentParser(description='Set up BigQuery tables for CityPulse')
    parser.add_argument('--project', required=True, help='GCP project ID')
    parser.add_argument('--dataset', default='citypulse', help='BigQuery dataset ID')
    parser.add_argument('--credentials', help='Path to service account JSON key file')

    args = parser.parse_args()

    if args.credentials:
        credentials = service_account.Credentials.from_service_account_file(args.credentials)
        client = bigquery.Client(project=args.project, credentials=credentials)
    else:
        client = bigquery.Client(project=args.project)

    dataset_id = args.dataset
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists.")
    except exceptions.NotFound:
        print(f"Creating dataset {dataset_id}...")
        client.create_dataset(bigquery.Dataset(dataset_ref))

    schema_mapping = {
        'events': 'event_schema.json',
        'user_profiles': 'user_profile_schema.json',
        'user_feedback': 'feedback_schema.json'
    }

    schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')
    for table_name, schema_file in schema_mapping.items():
        schema_path = os.path.join(schemas_dir, schema_file)
        create_table(client, args.project, dataset_id, table_name, schema_path)

if __name__ == "__main__":
    main()
