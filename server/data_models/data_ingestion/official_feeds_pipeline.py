"""Pipeline for ingesting data from official city feeds."""

import logging
import os
import sys

# Add parent directories to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_models.data_ingestion.base_pipeline import BasePipeline, BasePipelineOptions
from data_models.utils.pipeline_args import add_common_pipeline_args
from shared_config import get_config

# Initialize config
config = get_config()


class OfficialFeedsPipelineOptions(BasePipelineOptions):
    """Options for the official feeds pipeline."""

    @classmethod
    def _add_argparse_args(cls, parser):
        """
        Adds official feeds pipeline-specific arguments to the argument parser.

        Args:
            parser: The argparse.ArgumentParser instance.
        """
        output_table_name = (
            f"{config.project_id}:{config.database.bigquery_dataset}." f"official_feeds"
        )
        add_common_pipeline_args(parser, default_output_table=output_table_name)


class OfficialFeedsPipeline(BasePipeline):
    """A pipeline for ingesting data from official city feeds."""

    def __init__(self, pipeline_options=None):
        """
        Initializes the OfficialFeedsPipeline.

        Args:
            pipeline_options: An instance of PipelineOptions.
        """
        super().__init__(OfficialFeedsPipelineOptions, pipeline_options)

    # No custom processing is needed for this pipeline because the base class
    # handles the entire workflow of reading, parsing, and writing to sinks.
    # The add_custom_processing hook is intentionally not implemented.


if __name__ == "__main__":
    # This script is designed to be executed as a Dataflow job.
    # It sets up and runs the official feeds ingestion pipeline.
    logging.getLogger().setLevel(logging.INFO)
    pipeline_options = OfficialFeedsPipelineOptions()
    pipeline = OfficialFeedsPipeline(pipeline_options)
    pipeline.run()
