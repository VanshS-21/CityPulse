"""Tests for the citizen report pipeline multimedia processing."""
import unittest
from unittest.mock import MagicMock, patch

import apache_beam as beam
import requests
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.testing.test_pipeline import TestPipeline as BeamTestPipeline
from apache_beam.testing.util import assert_that, equal_to, is_empty

from data_models.firestore_models.event import Event
from data_models.tests.common import MOCK_EVENT_DATA
from data_models.transforms.multimedia_processing import ProcessMultimedia

TEST_PIPELINE_OPTIONS = PipelineOptions([
    '--input_topic',
    'dummy',
    '--output_table',
    'dummy:dummy.dummy',
    '--schema_path',
    'dummy.json',
])


class ProcessMultimediaTest(unittest.TestCase):
    """Tests for the ProcessMultimedia DoFn."""

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

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = (
                p | beam.Create([event])
                | beam.ParDo(ProcessMultimedia(bucket_name=bucket_name))
                | beam.Map(lambda e: (e.id, e.metadata.get('media_gcs_uri'))))

            expected = [(event.id, expected_gcs_path)]
            assert_that(results, equal_to(expected))

    def test_process_multimedia_no_media_url(self):
        """Tests that events without a media URL are passed through unchanged."""
        event = Event(**MOCK_EVENT_DATA)

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = (p | beam.Create([event])
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

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = (p | beam.Create([event]) | beam.ParDo(
                ProcessMultimedia(
                    bucket_name='test-bucket')).with_outputs('dead_letter',
                                                              main='main'))

            assert_that(results.main, is_empty(), label='CheckMainIsEmpty')
            assert_that(results.dead_letter,
                        _check_dead_letter,
                        label='CheckDeadLetter')


if __name__ == '__main__':
    unittest.main()
