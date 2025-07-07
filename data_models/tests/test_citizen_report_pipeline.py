"""Tests for the citizen report pipeline including multimedia and AI processing."""
import unittest
from unittest.mock import MagicMock, patch

import apache_beam as beam
import requests
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.testing.util import assert_that, equal_to, is_empty

from data_models.firestore_models.event import Event
from data_models.tests.common import BaseBeamTest, MOCK_EVENT_DATA
from data_models.data_ingestion.ai_processing import ProcessWithAI
from data_models.data_ingestion.citizen_report_pipeline import CitizenReportPipeline, CitizenReportOptions
from data_models.transforms.multimedia_processing import ProcessMultimedia


class ProcessMultimediaTest(BaseBeamTest):
    """Tests for the ProcessMultimedia DoFn."""

    def get_pipeline_options(self):
        """Return pipeline options for the test."""
        return PipelineOptions([
            '--input_topic', 'dummy',
            '--output_table', 'dummy:dummy.dummy',
            '--schema_path', 'dummy.json'
        ])

    @patch('data_models.transforms.multimedia_processing.storage.Client')
    @patch('data_models.transforms.multimedia_processing.requests.Session')
    def test_process_multimedia_success(self, mock_requests_session,
                                      mock_storage_client):
        """Tests successful processing of an event with a media URL."""
        mock_response = MagicMock()
        mock_response.content = b'fake media content'
        mock_requests_session.return_value.get.return_value = mock_response

        bucket_name = 'test-bucket'
        event_with_media = MOCK_EVENT_DATA.copy()
        event_with_media['metadata'] = {
            'media_url': 'http://example.com/image.jpg'
        }
        event = Event(**event_with_media)

        mock_blob = MagicMock()
        mock_blob.name = f'citizen_reports/{event.id}/image.jpg'
        mock_storage_client.return_value.bucket.return_value.blob.return_value = (
            mock_blob
        )

        expected_gcs_path = f'gs://{bucket_name}/{mock_blob.name}'

        results = (
            self.pipeline | beam.Create([event])
            | beam.ParDo(ProcessMultimedia(bucket_name=bucket_name))
            | beam.Map(lambda e: (e.id, e.metadata.get('media_gcs_uri'))))

        expected = [(event.id, expected_gcs_path)]
        assert_that(results, equal_to(expected))

    def test_process_multimedia_no_media_url(self):
        """Tests that events without a media URL are passed through unchanged."""
        event = Event(**MOCK_EVENT_DATA)

        results = (self.pipeline | beam.Create([event])
                   | beam.ParDo(ProcessMultimedia('test-bucket')))
        assert_that(results, equal_to([event]))

    @patch('data_models.transforms.multimedia_processing.requests.Session')
    def test_process_multimedia_download_failure(self, mock_requests_session):
        """Tests that media download failures are sent to the dead-letter queue."""
        mock_requests_session.return_value.get.side_effect = (
            requests.exceptions.RequestException('Download failed')
        )

        event_with_media = MOCK_EVENT_DATA.copy()
        event_with_media['metadata'] = {
            'media_url': 'http://example.com/image.jpg'
        }
        event = Event(**event_with_media)

        def _check_dead_letter(actual_dead_letters):
            assert len(actual_dead_letters) == 1
            dl = actual_dead_letters[0]
            assert isinstance(dl, dict)
            assert dl['pipeline_step'] == 'ProcessMultimedia'
            assert dl['raw_data'] == event.model_dump_json()
            assert dl['error_message'] == 'Download failed'

        results = (self.pipeline | beam.Create([event]) | beam.ParDo(
            ProcessMultimedia(
                bucket_name='test-bucket')).with_outputs('dead_letter',
                                                         main='main'))

        assert_that(results.main, is_empty(), label='CheckMainIsEmpty')
        assert_that(results.dead_letter,
                    _check_dead_letter,
                    label='CheckDeadLetter')


class CitizenReportPipelineTest(BaseBeamTest):
    """Tests for the integrated CitizenReportPipeline."""

    def get_pipeline_options(self):
        """Return pipeline options for the test."""
        return CitizenReportOptions([
            '--input_topic', 'dummy',
            '--output_table', 'dummy:dummy.dummy',
            '--schema_path', 'dummy.json',
            '--multimedia_bucket', 'test-bucket'
        ])

    @patch('data_models.data_ingestion.ai_processing.vertexai.GenerativeModel')
    @patch('data_models.data_ingestion.ai_processing.storage.Client')
    @patch('data_models.transforms.multimedia_processing.storage.Client')
    @patch('data_models.transforms.multimedia_processing.requests.Session')
    def test_integrated_pipeline(self, mock_requests_session, mock_mm_storage_client,
                               mock_ai_storage_client, mock_generative_model):
        """Tests the integrated pipeline with both multimedia and AI processing."""
        # Mock multimedia processing
        mock_response = MagicMock()
        mock_response.content = b'fake media content'
        mock_requests_session.return_value.get.return_value = mock_response

        mock_mm_blob = MagicMock()
        mock_mm_blob.name = 'citizen_reports/test-id/image.jpg'
        mock_mm_storage_client.return_value.bucket.return_value.blob.return_value = mock_mm_blob

        # Mock AI processing
        mock_ai_response = MagicMock()
        mock_ai_response.text = '{"summary": "AI summary", "category": "TRAFFIC", "image_tags": ["tag1", "tag2"]}'
        mock_generative_model.return_value.generate_content.return_value = mock_ai_response

        # Create test pipeline
        pipeline_options = self.get_pipeline_options()
        pipeline = CitizenReportPipeline(pipeline_options)

        # Create test event
        event_with_media = MOCK_EVENT_DATA.copy()
        event_with_media['metadata'] = {
            'media_url': 'http://example.com/image.jpg'
        }
        event = Event(**event_with_media)

        # Test custom processing
        pcoll = self.pipeline | beam.Create([event])
        processed, dead_letters = pipeline.add_custom_processing(pcoll)

        # Verify processed events have both multimedia and AI processing applied
        def check_processed(events):
            self.assertEqual(len(events), 1)
            processed_event = events[0]
            self.assertIn('media_gcs_uri', processed_event.metadata)
            self.assertEqual(processed_event.ai_summary, 'AI summary')
            self.assertEqual(processed_event.ai_category, 'TRAFFIC')
            self.assertEqual(processed_event.ai_image_tags, ['tag1', 'tag2'])

        assert_that(processed, check_processed, label='CheckProcessed')
        assert_that(dead_letters, is_empty(), label='CheckDeadLetters')


if __name__ == '__main__':
    unittest.main()
