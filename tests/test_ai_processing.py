"""E2E test for the AI processing pipeline."""
import os
import sys
from unittest.mock import patch, MagicMock
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions


# Add the project root to the Python path to allow importing project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_models.data_ingestion.ai_processing import ProcessWithAI
from data_models.core import config
from data_models.tests.common import BaseBeamTest

# --- Mock Data ---
# Using a public domain image of a pothole for testing.
MOCK_EVENT = {
    'event_id': 'mock_event_123',
    'description': 'There is a large and dangerous pothole on the main road near the city park. It has already caused damage to several cars.',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/8/86/Pothole_in_Villeray%2C_Montr%C3%A9al.jpg', # Example image URL
}

@patch('data_models.data_ingestion.ai_processing.storage.Client')
@patch('data_models.data_ingestion.ai_processing.ImageGenerationModel')
@patch('data_models.data_ingestion.ai_processing.GenerativeModel')
class TestAIProcessing(BaseBeamTest):

    def get_pipeline_options(self):
        return PipelineOptions(['--runner=DirectRunner'])

    def test_run_pipeline(self, mock_generative_model, mock_image_generation_model, mock_storage_client):
        """Runs a local Beam pipeline to test the ProcessWithAI DoFn."""

        # Configure the mocks
        mock_generative_model_instance = mock_generative_model.return_value
        mock_generative_model_instance.generate_content_async.return_value.text = '{"summary": "A pothole.", "category": "Road Hazard"}'

        mock_image_gen_model_instance = mock_image_generation_model.from_pretrained.return_value
        mock_image_gen_model_instance.generate_images_async.return_value = [MagicMock(_image_bytes=b'fake_image_bytes')]

        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket_instance = mock_storage_client_instance.bucket.return_value
        mock_blob_instance = mock_bucket_instance.blob.return_value
        mock_blob_instance.public_url = "http://fake.public.url/icon.png"

        # We need to set up mock config values for the test
        # In a real test suite, you'd use a mock library or a test config file.
        # Replace these with your actual project details if they differ.
        config.PROJECT_ID = "citypulse-21"
        config.GCP_REGION = "us-central1"
        # This bucket must exist in your GCP project for the test to pass.
        config.GCS_GENERATED_IMAGES_BUCKET = "citypulse-21-generated-images"

        events = self.pipeline | 'CreateMockEvent' >> beam.Create([MOCK_EVENT])

        processed_events = events | 'ProcessWithAI' >> beam.ParDo(ProcessWithAI())

        def write_to_file(element):
            import json
            with open('tests/test_output.json', 'w') as f:
                json.dump(element, f, indent=2)
            print("Test output written to tests/test_output.json")

        processed_events | 'WriteResults' >> beam.Map(write_to_file)
