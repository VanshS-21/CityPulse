"""Pipeline for ingesting and analyzing social media data."""

import json
import logging

import apache_beam as beam
from apache_beam.pvalue import TaggedOutput
from google.api_core import exceptions
from google.cloud import language_v1
from pydantic import ValidationError

from data_models.core import config
from data_models.data_ingestion.base_pipeline import BasePipeline, BasePipelineOptions
from data_models.firestore_models.event import Event
from data_models.utils.pipeline_args import add_common_pipeline_args


class SocialMediaPipelineOptions(BasePipelineOptions):
    """Options for the social media pipeline."""

    @classmethod
    def _add_argparse_args(cls, parser):
        """
        Adds social media pipeline-specific arguments to the argument parser.

        Args:
            parser: The argparse.ArgumentParser instance.
        """
        output_table_name = (
            f'{config.PROJECT_ID}:{config.BIGQUERY_DATASET}.'
            f'{config.BIGQUERY_TABLE_SOCIAL_MEDIA}'
        )
        add_common_pipeline_args(parser, default_output_table=output_table_name)


# pylint: disable=abstract-method
class ParseSocialMediaEvent(beam.DoFn):
    """Parses a raw social media event into an Event object."""

    def process(self, element, *args, **kwargs):
        """
        Processes a single element, parsing it from JSON to an Event object.

        Yields:
            - A Pydantic Event object on successful parsing.
            - A TaggedOutput to 'dead_letter' on failure.
        """
        try:
            data = json.loads(element.decode('utf-8'))
            if 'event_id' in data:
                data['id'] = data.pop('event_id')
            event = Event(**data)
            yield event
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            error_payload = {
                'pipeline_step': 'ParseSocialMediaEvent',
                'raw_data': element.decode('utf-8', 'ignore'),
                'error_message': str(e)
            }
            logging.error('Error parsing social media event: %s', e)
            yield TaggedOutput('dead_letter', error_payload)


# pylint: disable=abstract-method
class AnalyzeSentiment(beam.DoFn):
    """Analyzes the sentiment of the event description."""

    def __init__(self):
        """Initializes the AnalyzeSentiment DoFn."""
        super().__init__()
        self.client = None

    def setup(self):
        """Initializes the LanguageServiceClient in the worker."""
        self.client = language_v1.LanguageServiceClient()

    def process(self, element: Event, *args, **kwargs):
        """
        Processes a single element by analyzing its sentiment.

        Yields:
            - The enriched Event object on success.
            - A TaggedOutput to 'dead_letter' on failure.
        """
        try:
            document = language_v1.Document(
                content=element.description, type_=language_v1.Document.Type.PLAIN_TEXT
            )
            sentiment = self.client.analyze_sentiment(document=document).document_sentiment
            element.metadata['sentiment_score'] = sentiment.score
            element.metadata['sentiment_magnitude'] = sentiment.magnitude
            yield element
        except (exceptions.GoogleAPICallError, ValueError) as e:
            error_payload = {
                'pipeline_step': 'AnalyzeSentiment',
                'raw_data': element.model_dump_json(),
                'error_message': str(e)
            }
            logging.error('Error during sentiment analysis for event %s: %s', element.id, e)
            yield TaggedOutput('dead_letter', error_payload)


class SocialMediaPipeline(BasePipeline):
    """A pipeline for ingesting and analyzing social media data."""

    def __init__(self, pipeline_options=None):
        """
        Initializes the SocialMediaPipeline.

        Args:
            pipeline_options: An instance of PipelineOptions.
        """
        super().__init__(SocialMediaPipelineOptions, pipeline_options)

    def get_parser_dofn(self):
        """Returns the DoFn to use for parsing social media events."""
        return ParseSocialMediaEvent()

    def add_custom_processing(self, pcollection):
        """
        Adds sentiment analysis processing to the pipeline.

        Args:
            pcollection: A PCollection of parsed Event objects.

        Returns:
            A tuple containing the main PCollection of processed events and a
            PCollection for any dead-letter records from this step.
        """
        analyzed_events = pcollection | 'Analyze Sentiment' >> beam.ParDo(
            AnalyzeSentiment()
        ).with_outputs('dead_letter', main='analyzed')

        return analyzed_events.analyzed, analyzed_events.dead_letter


if __name__ == '__main__':
    # This script is designed to be executed as a Dataflow job.
    # It sets up and runs the social media ingestion pipeline.
    logging.getLogger().setLevel(logging.INFO)
    pipeline_options = SocialMediaPipelineOptions()
    pipeline = SocialMediaPipeline(pipeline_options)
    pipeline.run()
