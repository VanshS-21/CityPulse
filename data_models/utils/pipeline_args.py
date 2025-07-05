"""Utility functions for defining and parsing pipeline arguments."""

import argparse

def add_common_pipeline_args(parser: argparse.ArgumentParser, default_output_table: str) -> None:
    """Adds common pipeline arguments to the parser."""
    parser.add_argument(
        '--output_table',
        help='BigQuery table to write to.',
        default=default_output_table
    )
    parser.add_argument(
        '--schema_path',
        help='Path to the BigQuery schema file.',
        default='data_models/schemas/event_schema.json'
    )
