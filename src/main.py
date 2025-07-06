"""A simple Apache Beam pipeline."""
import logging
import os
from dotenv import load_dotenv
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

load_dotenv()


def run_pipeline():
    """Defines and runs the Apache Beam pipeline."""
    # Configure pipeline options
    pipeline_options = PipelineOptions([
        '--runner=DirectRunner',  # Use DirectRunner for local testing
        f'--project={os.getenv("GCP_PROJECT_ID")}',
        f'--temp_location={os.getenv("GCP_BUCKET_TEMP")}',
        f'--staging_location={os.getenv("GCP_BUCKET_STAGING")}',
    ])

    # Create and run pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        (p
         | 'Create Data' >> beam.Create(['Hello', 'World', 'Apache', 'Beam'])
         | 'Add Timestamp' >> beam.Map(lambda x: f"{x} - processed")
         | 'Print Results' >> beam.Map(print)
        )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run_pipeline()
