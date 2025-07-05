"""Pipeline for ingesting data from citizen reports."""

import logging

import apache_beam as beam

from data_models.core import config
from data_models.data_ingestion.base_pipeline import BasePipeline, BasePipelineOptions
from data_models.transforms.multimedia_processing import ProcessMultimedia
from data_models.utils.pipeline_args import add_common_pipeline_args


class CitizenReportOptions(BasePipelineOptions):
    """Options for the citizen report pipeline."""

    @classmethod
    def _add_argparse_args(cls, parser):
        """
        Adds citizen report pipeline-specific arguments to the argument parser.

        Args:
            parser: The argparse.ArgumentParser instance.
        """
        parser.add_argument(
            '--multimedia_bucket',
            help='GCS bucket for multimedia uploads.',
            default=config.MULTIMEDIA_BUCKET_NAME)

        output_table_name = (
            f'{config.PROJECT_ID}:{config.BIGQUERY_DATASET}.'
            f'{config.BIGQUERY_TABLE_CITIZEN_REPORTS}'
        )
        add_common_pipeline_args(parser, default_output_table=output_table_name)


class CitizenReportPipeline(BasePipeline):
    """A pipeline for ingesting citizen reports."""

    def __init__(self, pipeline_options=None):
        """
        Initializes the CitizenReportPipeline.

        Args:
            pipeline_options: An instance of PipelineOptions.
        """
        super().__init__(CitizenReportOptions, pipeline_options)

    def add_custom_processing(self, pcollection):
        """
        Adds multimedia processing steps to the pipeline.

        This method takes a PCollection of parsed event data, processes any
        multimedia URLs found within the events, and uploads them to GCS.

        Args:
            pcollection: A PCollection of parsed Event objects.

        Returns:
            A tuple containing the main PCollection of processed events and a
            PCollection for any dead-letter records from this step.
        """
        results = pcollection | 'Process Multimedia' >> beam.ParDo(
            ProcessMultimedia(self.custom_options.multimedia_bucket)
        ).with_outputs('dead_letter', main='main')

        return results.main, results.dead_letter


if __name__ == '__main__':
    # This script is designed to be executed as a Dataflow job.
    # It sets up and runs the citizen report ingestion pipeline.
    logging.getLogger().setLevel(logging.INFO)
    pipeline_options = CitizenReportOptions()
    pipeline = CitizenReportPipeline(pipeline_options)
    pipeline.run()
