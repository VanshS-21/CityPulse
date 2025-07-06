import argparse
import json
import logging
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import TaggedOutput

# --- Constants ---

# Schema for the main BigQuery table
MAIN_TABLE_SCHEMA = {
    "fields": [
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "user_id", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "event_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "processing_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    ]
}

# Schema for the dead-letter BigQuery table
DEAD_LETTER_TABLE_SCHEMA = {
    "fields": [
        {"name": "payload", "type": "STRING", "mode": "NULLABLE"},
        {"name": "reason", "type": "STRING", "mode": "NULLABLE"},
        {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    ]
}

# --- PTransforms ---

class ParseAndValidate(beam.DoFn):
    """
    Parses JSON strings, validates against a schema, and routes to valid/invalid outputs.
    """
    OUTPUT_TAG_VALID = 'valid'
    OUTPUT_TAG_INVALID = 'invalid'

    def process(self, element: bytes):
        """
        Processes each Pub/Sub message.

        Args:
            element: The message payload from Pub/Sub, as bytes.
        """
        try:
            # 1. Decode and Parse JSON
            payload_str = element.decode('utf-8')
            record = json.loads(payload_str)
        except json.JSONDecodeError:
            yield TaggedOutput(
                self.OUTPUT_TAG_INVALID,
                {
                    "payload": element.decode('utf-8', errors='ignore'),
                    "reason": "Malformed JSON",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            return
        except Exception as e:
            yield TaggedOutput(
                self.OUTPUT_TAG_INVALID,
                {
                    "payload": element.decode('utf-8', errors='ignore'),
                    "reason": f"Unknown parsing error: {e}",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            return

        # 2. Validate Schema
        required_fields = {
            "event_id": str,
            "user_id": int,
            "event_timestamp": str,
        }
        missing_fields = [field for field in required_fields if field not in record]
        if missing_fields:
            reason = f"Missing required field(s): {', '.join(missing_fields)}"
            yield TaggedOutput(
                self.OUTPUT_TAG_INVALID,
                {"payload": payload_str, "reason": reason, "timestamp": datetime.utcnow().isoformat()},
            )
            return

        type_errors = []
        for field, expected_type in required_fields.items():
            if not isinstance(record.get(field), expected_type):
                type_errors.append(
                    f"Invalid type for '{field}': expected {expected_type.__name__}, "
                    f"got {type(record.get(field)).__name__}"
                )
        if type_errors:
            reason = f"Schema validation failed: {'; '.join(type_errors)}"
            yield TaggedOutput(
                self.OUTPUT_TAG_INVALID,
                {"payload": payload_str, "reason": reason, "timestamp": datetime.utcnow().isoformat()},
            )
            return

        # If all checks pass, yield to the valid output
        yield record


class TransformValidRecord(beam.DoFn):
    """
    Transforms a validated record by parsing timestamps and adding metadata.
    """
    def process(self, element: dict):
        """
        Args:
            element: A dictionary representing a valid record.
        """
        try:
            # 1. Parse event_timestamp
            # Assuming ISO 8601 format, e.g., "2023-01-01T12:00:00Z"
            # BigQuery expects a specific string format or a datetime object.
            # We will parse it to ensure it's valid and then let Beam's BQ sink handle it.
            try:
                parsed_event_timestamp = datetime.fromisoformat(element["event_timestamp"].replace("Z", "+00:00"))
            except ValueError:
                # Handle cases where the timestamp is not in the expected format
                logging.warning(f"Could not parse timestamp: {element['event_timestamp']}. Using current time instead.")
                parsed_event_timestamp = datetime.utcnow()

            # 2. Add processing_timestamp
            processing_timestamp = datetime.utcnow()

            # 3. Create the final record
            transformed_record = {
                "event_id": element["event_id"],
                "user_id": element["user_id"],
                "event_timestamp": parsed_event_timestamp.isoformat(),
                "processing_timestamp": processing_timestamp.isoformat(),
            }
            yield transformed_record
        except (ValueError, TypeError) as e:
            # This is an unexpected error for a "valid" record, but we should handle it.
            # It could be routed to another dead-letter queue if necessary.
            logging.error(f"Error transforming supposedly valid record: {element}. Error: {e}")
            # For simplicity, we drop it here, but in a real scenario, it might go to another sink.


# --- Pipeline Definition ---

def run(
    subscription: str,
    main_table: str,
    dead_letter_table: str,
    pipeline_args: list[str] = None,
):
    """
    Defines and runs the Apache Beam pipeline.

    Args:
        subscription: The Cloud Pub/Sub subscription to read from.
        main_table: The BigQuery table for valid records (e.g., project:dataset.table).
        dead_letter_table: The BigQuery table for invalid records.
        pipeline_args: Additional arguments for the pipeline.
    """
    pipeline_options = PipelineOptions(pipeline_args, save_main_session=True, streaming=True)

    with beam.Pipeline(options=pipeline_options) as p:
        # 1. Read from Pub/Sub
        messages = p | "ReadFromPubSub" >> beam.io.ReadFromPubSub(
            subscription=subscription
        ).with_output_types(bytes)

        # 2. Parse and Validate JSON
        # 2. Parse and Validate JSON
        # The result of this transform will be a PCollection of dictionaries.
        # The main output will contain valid records, and the tagged output
        # will contain invalid records.
        processed_records = messages | "ParseAndValidate" >> beam.ParDo(
            ParseAndValidate()
        ).with_outputs(ParseAndValidate.OUTPUT_TAG_INVALID, main="valid_records")

        valid_records = processed_records.valid_records
        invalid_records = processed_records[ParseAndValidate.OUTPUT_TAG_INVALID]

        # 3. Transform Valid Records
        transformed_records = valid_records | "TransformValidRecords" >> beam.ParDo(TransformValidRecord())

        # 4. Write Valid Records to BigQuery
        transformed_records | "WriteValidToBigQuery" >> beam.io.WriteToBigQuery(
            main_table,
            schema=MAIN_TABLE_SCHEMA,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
        )

        # 5. Write Invalid Records to BigQuery
        (
            invalid_records
            | "ExtractPayload" >> beam.Map(lambda x: {"payload": x.get("payload", ""), "reason": x.get("reason", ""), "timestamp": x.get("timestamp", "")})
            | "WriteInvalidToBigQuery" >> beam.io.WriteToBigQuery(
                dead_letter_table,
                schema=DEAD_LETTER_TABLE_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            )
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subscription",
        required=True,
        help="Google Cloud Pub/Sub subscription to read from (e.g., projects/your-project/subscriptions/your-subscription).",
    )
    parser.add_argument(
        "--main_table",
        required=True,
        help="BigQuery table for valid data (e.g., your-project:your_dataset.main_table).",
    )
    parser.add_argument(
        "--dead_letter_table",
        required=True,
        help="BigQuery table for invalid data (e.g., your-project:your_dataset.dead_letter_table).",
    )
    known_args, pipeline_args = parser.parse_known_args()

    run(
        subscription=known_args.subscription,
        main_table=known_args.main_table,
        dead_letter_table=known_args.dead_letter_table,
        pipeline_args=pipeline_args,
    )