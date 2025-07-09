"""Pipeline for ingesting and processing IoT sensor data."""

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
from data_models.utils.pipeline_args import add_common_pipeline_args


class IotPipelineOptions(BasePipelineOptions):
    """Options for the IoT pipeline."""

    @classmethod
    def _add_argparse_args(cls, parser):
        """
        Adds IoT pipeline-specific arguments to the argument parser.

        Args:
            parser: The argparse.ArgumentParser instance.
        """
        output_table_name = (
            f"{config.project_id}:{config.database.bigquery_dataset}." f"iot_data"
        )
        add_common_pipeline_args(parser, default_output_table=output_table_name)


class IotPipeline(BasePipeline):
    """A pipeline for ingesting and processing IoT sensor data."""

    def __init__(self, pipeline_options=None):
        """
        Initializes the IotPipeline.

        Args:
            pipeline_options: An instance of PipelineOptions.
        """
        super().__init__(IotPipelineOptions, pipeline_options)

    def add_custom_processing(self, pcollection):
        """
        Adds AI processing to the pipeline.

        This method takes a PCollection of parsed event data and applies AI
        processing to enrich it with insights like summarization and categorization.

        Args:
            pcollection: A PCollection of parsed Event objects.

        Returns:
            A tuple containing the main PCollection of processed events and a
            PCollection for any dead-letter records from this step.
        """
        ai_results = (
            pcollection
            | "Batch Elements" >> beam.GroupIntoBatches(batch_size=10)
            | "AI Processing"
            >> beam.ParDo(ProcessWithAI()).with_outputs("dead_letter", main="processed")
        )

        return ai_results.processed, ai_results.dead_letter


if __name__ == "__main__":
    # This script is designed to be executed as a Dataflow job.
    # It sets up and runs the IoT sensor data ingestion pipeline.
    logging.getLogger().setLevel(logging.INFO)
    pipeline_options = IotPipelineOptions()
    pipeline = IotPipeline(pipeline_options)
    pipeline.run()
