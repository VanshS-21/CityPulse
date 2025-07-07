"""Base classes and components for data ingestion pipelines."""

import datetime
import json
import logging

import apache_beam as beam
from apache_beam import window
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.pvalue import TaggedOutput
from google.api_core import exceptions
from pydantic import ValidationError

from data_models.core import config
from data_models.firestore_models.event import Event
from data_models.services.firestore_service import FirestoreService


def format_for_bigquery(event):
    """Formats an Event object for BigQuery insertion."""
    data = event.to_firestore_dict()

    # Convert metadata to JSON string for BigQuery JSON field
    if 'metadata' in data and data['metadata'] is not None:
        data['metadata'] = json.dumps(data['metadata'])

    return data


class BasePipelineOptions(PipelineOptions):
    """Options for a base data ingestion pipeline."""
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            '--input_topic',
            help='The Cloud Pub/Sub topic to read from.',
            default=None
        )


        parser.add_argument(
            '--dead_letter_table',
            help='BigQuery table for dead-letter records. '
                 'Defaults to <dataset>.dead_letter_events.',
            default=f'{config.PROJECT_ID}:{config.BIGQUERY_DATASET}.dead_letter_events'
        )

# pylint: disable=abstract-method
class ParseEvent(beam.DoFn):
    """Parses a JSON string into a Pydantic Event object."""

    def process(self, element):
        """
        Processes a single element, parsing it from JSON to an Event object.

        Yields:
            - A Pydantic Event object on successful parsing.
            - A TaggedOutput to 'dead_letter' on failure.
        """
        try:
            data = json.loads(element.decode('utf-8'))
            event = Event(**data)
            yield event
        except (json.JSONDecodeError, ValidationError) as e:
            error_payload = {
                'pipeline_step': 'ParseEvent',
                'raw_data': element.decode('utf-8', 'ignore'),
                'error_message': str(e)
            }
            logging.error('Error parsing event: %s', e)
            yield TaggedOutput('dead_letter', error_payload)


# pylint: disable=abstract-method
class WriteToFirestore(beam.DoFn):
    """Writes an Event object to Firestore and outputs the original event on success."""

    def __init__(self, project_id: str = None):
        super().__init__()
        self.project_id = project_id
        self.firestore_service = None

    def setup(self):
        """Initializes the FirestoreService client in the worker."""
        self.firestore_service = FirestoreService(project_id=self.project_id)

    def process(self, element: Event):
        """
        Processes a single element by writing it to Firestore.

        Yields:
            - The original element on successful write.
            - A TaggedOutput to 'dead_letter' on failure.
        """
        try:
            self.firestore_service.add_document(element)
            yield element
        except (exceptions.GoogleAPICallError, ValueError) as e:
            error_payload = {
                'pipeline_step': 'WriteToFirestore',
                'raw_data': element.model_dump_json(),
                'error_message': str(e)
            }
            logging.error('Error writing to Firestore: %s', e)
            yield beam.pvalue.TaggedOutput('dead_letter', error_payload)


class BasePipeline:
    """
    A base class for data ingestion pipelines, providing a common structure for
    reading from Pub/Sub, parsing data, and writing to Firestore and BigQuery.
    """

    def __init__(self, options_class, pipeline_options=None):
        """
        Initializes the pipeline with the given options.

        Args:
            options_class: The class defining custom pipeline options.
            pipeline_options: An instance of PipelineOptions, or the class itself.
        """
        # If pipeline_options is a class, instantiate it. This handles the way
        # the from_options factory method calls the constructor in tests.
        if isinstance(pipeline_options, type):
            # Pass empty flags to avoid parsing sys.argv, which can conflict
            # with pytest's arguments.
            self.pipeline_options = pipeline_options(flags=[])
        else:
            # In production, pipeline_options would be an instance or None.
            self.pipeline_options = pipeline_options or PipelineOptions()

        self.custom_options = self.pipeline_options.view_as(options_class)
        self.google_cloud_options = self.pipeline_options.view_as(
            GoogleCloudOptions)

        if not self.google_cloud_options.project:
            self.google_cloud_options.project = config.PROJECT_ID

        self.firestore_service = FirestoreService(
            project_id=self.google_cloud_options.project)

    def _read_from_pubsub(self, pipeline):
        """Reads messages from a Pub/Sub topic."""
        topic_path = (
            f'projects/{self.google_cloud_options.project}/topics/'
            f'{self.custom_options.input_topic}'
        )
        return pipeline | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
            topic=topic_path
        ).with_output_types(bytes)

    def _parse_and_validate(self, pcollection):
        """Parses and validates incoming messages."""
        return pcollection | 'Parse and Validate' >> beam.ParDo(
            self.get_parser_dofn()
        ).with_outputs('dead_letter', main='parsed_events')

    def _write_to_firestore(self, pcollection):
        """Writes valid events to Firestore."""
        return pcollection | 'Write to Firestore' >> beam.ParDo(
            WriteToFirestore(project_id=self.google_cloud_options.project)
        ).with_outputs('dead_letter', main='firestore_events')



    def _write_to_bigquery(self, pcollection):
        """Writes the final processed events to BigQuery."""
        with open(self.custom_options.schema_path, encoding="utf-8") as f:
            schema = json.load(f)

        return pcollection | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
            self.custom_options.output_table,
            schema={'fields': schema['fields']},
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS  # Fix for streaming data
        )

    def _handle_dead_letters(self, dead_letter_pcollections):
        """
        Flattens a list of PCollections containing dead-letter records and writes them
        to a specified BigQuery table for later analysis.
        """
        valid_dead_letters = [dl for dl in dead_letter_pcollections if dl]
        if not valid_dead_letters:
            return

        all_dead_letters = valid_dead_letters | 'FlattenDeadLetters' >> beam.Flatten()

        def format_dead_letter_for_bq(element):
            """Formats a failed element into a dictionary for the dead-letter table."""


            if isinstance(element, dict):
                return {
                    'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'pipeline_step': element.get('pipeline_step', 'unknown'),
                    'raw_data': str(element.get('raw_data')),
                    'error_message': str(element.get('error_message', 'unknown'))
                }

            raw_data = str(element)
            try:
                if isinstance(element, bytes):
                    raw_data = element.decode('utf-8', 'ignore')
            except (UnicodeDecodeError, AttributeError):
                pass

            return {
                'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'pipeline_step': 'unknown',
                'raw_data': raw_data,
                'error_message': 'unknown'
            }

        formatted_errors = (
            all_dead_letters | 'FormatDeadLetter' >> beam.Map(format_dead_letter_for_bq)
        )

        with open('data_models/schemas/dead_letter_schema.json', encoding="utf-8") as f:
            schema = json.load(f)

        _ = formatted_errors | 'WriteDeadLetterToBigQuery' >> beam.io.WriteToBigQuery(
            self.custom_options.dead_letter_table,
            schema={'fields': schema['fields']},
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS  # Fix for streaming data
        )

    def build_pipeline(self, pipeline):
        """Builds the core pipeline structure."""
        raw_events = self._read_from_pubsub(pipeline)
        parsed_data = self._parse_and_validate(raw_events)

        processed_data, custom_dead_letters = self.add_custom_processing(
            parsed_data.parsed_events
        )

        firestore_results = self._write_to_firestore(processed_data)

        bq_events = firestore_results.firestore_events | 'ToDict' >> beam.Map(
            format_for_bigquery
        )

        # For streaming pipelines, apply a window to batch writes to BigQuery.
        windowed_events = bq_events | 'WindowInto' >> beam.WindowInto(
            window.FixedWindows(60)  # 60-second windows
        )

        self._write_to_bigquery(windowed_events)

        self._handle_dead_letters([
            parsed_data.dead_letter,
            custom_dead_letters,
            firestore_results.dead_letter
        ])

    def get_parser_dofn(self):
        """Returns the DoFn to use for parsing events. Subclasses can override this."""
        return ParseEvent()

    def add_custom_processing(self, pcollection):
        """
        Hook for subclasses to add their own processing steps.

        Returns:
            A tuple containing the processed PCollection and any dead-letter PCollection.
        """
        return pcollection, None

    def run(self):
        """Runs the pipeline."""
        with beam.Pipeline(options=self.pipeline_options) as pipeline:
            self.build_pipeline(pipeline)

    @classmethod
    def from_options(cls, options_class):
        """
        Creates a pipeline instance from a given options class.

        Args:
            options_class: The class defining custom pipeline options.

        Returns:
            An instance of the pipeline.
        """
        return cls(options_class)
