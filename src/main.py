"""Main entry point for the CityPulse backend application."""
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Import the IoT pipeline
from data_models.data_ingestion.iot_pipeline import IotPipeline, IotPipelineOptions

# Load environment variables from .env file
load_dotenv()


def run_iot_pipeline():
    """Runs the IoT data processing pipeline."""
    # Configure pipeline options
    pipeline_options = PipelineOptions([
        '--runner=DirectRunner',  # Use DirectRunner for local testing
        f'--project={os.getenv("GCP_PROJECT_ID")}',
        f'--temp_location={os.getenv("GCP_BUCKET_TEMP")}',
        f'--staging_location={os.getenv("GCP_BUCKET_STAGING")}',
        '--input_topic=iot-data',  # The Pub/Sub topic to read from
        '--schema_path=data_models/schemas/event_schema.json',  # Path to the schema file
    ])

    # Create and run the IoT pipeline
    pipeline = IotPipeline(pipeline_options)
    pipeline.run()


def run_demo_pipeline():
    """Runs a simple demo pipeline for testing."""
    # Configure pipeline options
    pipeline_options = PipelineOptions([
        '--runner=DirectRunner',  # Use DirectRunner for local testing
        f'--project={os.getenv("GCP_PROJECT_ID")}',
        f'--temp_location={os.getenv("GCP_BUCKET_TEMP")}',
        f'--staging_location={os.getenv("GCP_BUCKET_STAGING")}',
    ])

    # Create and run a simple pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        (p
         | 'Create Data' >> beam.Create(['Hello', 'World', 'Apache', 'Beam'])
         | 'Add Timestamp' >> beam.Map(lambda x: f"{x} - processed at {datetime.now()}")
         | 'Print Results' >> beam.Map(print)
        )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Starting CityPulse backend application")
    
    # Run the IoT pipeline
    try:
        run_iot_pipeline()
    except Exception as e:
        logging.error(f"Error running IoT pipeline: {e}")
        logging.info("Falling back to demo pipeline")
        run_demo_pipeline()
