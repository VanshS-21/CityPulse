"""Pipeline for ingesting data from citizen reports."""

import logging
import os
import sys

import apache_beam as beam

# Add parent directories to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared_config import get_config

# Initialize config
config = get_config()
from data_models.data_ingestion.ai_processing import ProcessWithAI
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
            "--multimedia_bucket",
            help="GCS bucket for multimedia uploads.",
            default=config.storage.get_media_bucket_name(),
        )

        output_table_name = (
            f"{config.project_id}:{config.database.bigquery_dataset}."
            f"citizen_reports"
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
        multimedia_results = pcollection | "Process Multimedia" >> beam.ParDo(
            ProcessMultimedia(self.custom_options.multimedia_bucket)
        ).with_outputs("dead_letter", main="main")

        ai_results = multimedia_results.main | "Process with AI" >> beam.ParDo(
            ProcessWithAI()
        ).with_outputs("dead_letter", main="main")

        # Merge dead-letter PCollections
        dead_letters = (
            multimedia_results.dead_letter,
            ai_results.dead_letter,
        ) | "Flatten Dead Letters" >> beam.Flatten()

        return ai_results.main, dead_letters


if __name__ == "__main__":
    # This script is designed to be executed as a Dataflow job.
    # It sets up and runs the citizen report ingestion pipeline.
    logging.getLogger().setLevel(logging.INFO)
    pipeline_options = CitizenReportOptions()
    pipeline = CitizenReportPipeline(pipeline_options)
    pipeline.run()
