import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import logging
import os
import sys

# Add the project root to the Python path to allow importing project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_models.data_ingestion.ai_processing import ProcessWithAI
from data_models.core import config

# --- Mock Data ---
# Using a public domain image of a pothole for testing.
MOCK_EVENT = {
    'event_id': 'mock_event_123',
    'description': 'There is a large and dangerous pothole on the main road near the city park. It has already caused damage to several cars.',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/8/86/Pothole_in_Villeray%2C_Montr%C3%A9al.jpg', # Example image URL
}

def run_test_pipeline():
    """Runs a local Beam pipeline to test the ProcessWithAI DoFn."""
    
    # We need to set up mock config values for the test
    # In a real test suite, you'd use a mock library or a test config file.
    # Replace these with your actual project details if they differ.
    config.PROJECT_ID = "citypulse-21"
    config.GCP_REGION = "us-central1"
    # This bucket must exist in your GCP project for the test to pass.
    config.GCS_GENERATED_IMAGES_BUCKET = "citypulse-21-generated-images"

    pipeline_options = PipelineOptions(['--runner=DirectRunner'])

    with beam.Pipeline(options=pipeline_options) as p:
        events = p | 'CreateMockEvent' >> beam.Create([MOCK_EVENT])

        processed_events = events | 'ProcessWithAI' >> beam.ParDo(ProcessWithAI())

        def write_to_file(element):
            import json
            with open('tests/test_output.json', 'w') as f:
                json.dump(element, f, indent=2)
            print("Test output written to tests/test_output.json")

        processed_events | 'WriteResults' >> beam.Map(write_to_file)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    print("--- Starting AI Processing Test ---")
    run_test_pipeline()
    print("--- AI Processing Test Finished ---")
