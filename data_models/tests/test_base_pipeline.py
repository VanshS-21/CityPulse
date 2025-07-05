"""Tests for the base data processing pipeline components."""
import json
import logging
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.testing.test_pipeline import TestPipeline as BeamTestPipeline
from apache_beam.testing.util import assert_that, equal_to, is_empty
from google.api_core import exceptions as google_exceptions

from data_models.data_ingestion.base_pipeline import ParseEvent, WriteToFirestore
from data_models.firestore_models.event import Event
from data_models.tests.common import MOCK_EVENT_DATA


TEST_PIPELINE_OPTIONS = PipelineOptions([
    '--input_topic', 'dummy',
    '--output_table', 'dummy:dummy.dummy',
    '--schema_path', 'dummy.json',
])


class ParseEventTest(unittest.TestCase):
    """Tests for the ParseEvent DoFn."""

    @patch('data_models.firestore_models.event.datetime')
    def test_parse_event_success(self, mock_datetime):
        """Tests successful parsing of a valid event."""
        mock_dt = datetime(2025, 7, 3, 20, 39, 41, 428153)
        mock_datetime.utcnow = MagicMock(return_value=mock_dt)

        event_data_str = json.dumps(MOCK_EVENT_DATA).encode('utf-8')
        expected_event = Event(**MOCK_EVENT_DATA)

        def assert_event_data_equals(actual_events):
            assert len(actual_events) == 1
            actual_event = actual_events[0]

            # Timestamps are generated inside the DoFn, so we can't easily mock them.
            # Instead, we check for their presence and then compare the rest of the dict.
            actual_event_dict = actual_event.model_dump()
            for key in ['created_at', 'updated_at', 'start_time']:
                assert key in actual_event_dict
                del actual_event_dict[key]

            expected_dict = expected_event.model_dump()
            for key in ['created_at', 'updated_at', 'start_time']:
                del expected_dict[key]

            assert actual_event_dict == expected_dict

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            events = p | 'Create' >> beam.Create([event_data_str])
            parsed_events = events | 'Parse' >> beam.ParDo(ParseEvent())
            assert_that(parsed_events, assert_event_data_equals)

    def test_parse_event_invalid_json(self):
        """Tests that invalid JSON is sent to the dead-letter queue."""
        invalid_json_str = b'{"key": "value"'

        def _check_dead_letter(actual_dead_letters):
            assert len(actual_dead_letters) == 1
            dl = actual_dead_letters[0]
            assert isinstance(dl, dict)
            assert dl['pipeline_step'] == 'ParseEvent'
            assert dl['raw_data'] == invalid_json_str.decode('utf-8', 'ignore')
            assert 'error_message' in dl and dl['error_message']

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = p | beam.Create([invalid_json_str]) | beam.ParDo(
                ParseEvent()).with_outputs('dead_letter', main='parsed_events')
            assert_that(results.parsed_events, is_empty(),
                        label='CheckParsedIsEmpty')
            assert_that(results.dead_letter, _check_dead_letter,
                        label='CheckDeadLetter')

    def test_parse_event_validation_error(self):
        """Tests that events failing Pydantic validation are dead-lettered."""
        invalid_event_data = MOCK_EVENT_DATA.copy()
        del invalid_event_data['title']  # 'title' is a required field
        invalid_event_str = json.dumps(invalid_event_data).encode('utf-8')

        def _check_dead_letter(actual_dead_letters):
            assert len(actual_dead_letters) == 1
            dl = actual_dead_letters[0]
            assert isinstance(dl, dict)
            assert dl['pipeline_step'] == 'ParseEvent'
            assert dl['raw_data'] == invalid_event_str.decode('utf-8', 'ignore')
            assert 'error_message' in dl and 'validation error' in dl['error_message']

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = p | beam.Create([invalid_event_str]) | beam.ParDo(
                ParseEvent()).with_outputs('dead_letter', main='parsed_events')
            assert_that(results.parsed_events, is_empty(),
                        label='CheckParsedIsEmpty')
            assert_that(results.dead_letter, _check_dead_letter,
                        label='CheckDeadLetter')


class WriteToFirestoreTest(unittest.TestCase):
    """Tests for the WriteToFirestore DoFn."""

    @patch('data_models.data_ingestion.base_pipeline.FirestoreService')
    def test_write_to_firestore_success(self, mock_firestore_service_class):
        """Tests successful writing of an event to Firestore."""
        mock_firestore_service = mock_firestore_service_class.return_value
        event = Event(**MOCK_EVENT_DATA)
        expected_output = event

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = (
                p | beam.Create([event])
                | beam.ParDo(WriteToFirestore())
            )
            assert_that(results, equal_to([expected_output]))

        mock_firestore_service.add_document.assert_called_once_with(event)

    @patch('data_models.data_ingestion.base_pipeline.FirestoreService')
    def test_write_to_firestore_exception(self, mock_firestore_service_class):
        """Tests that Firestore write failures are sent to the dead-letter queue."""
        mock_firestore_service = mock_firestore_service_class.return_value
        mock_firestore_service.add_document.side_effect = (
            google_exceptions.GoogleAPICallError('Firestore Error')
        )

        event = Event(**MOCK_EVENT_DATA)

        def _check_dead_letter(actual_dead_letters):
            assert len(actual_dead_letters) == 1
            dl = actual_dead_letters[0]
            assert isinstance(dl, dict)
            assert dl['pipeline_step'] == 'WriteToFirestore'
            assert dl['raw_data'] == event.model_dump_json()
            assert dl['error_message'] == 'None Firestore Error'

        with BeamTestPipeline(options=TEST_PIPELINE_OPTIONS) as p:
            results = (
                p | beam.Create([event])
                | beam.ParDo(WriteToFirestore()).with_outputs('dead_letter', main='main')
            )
            assert_that(results.main, is_empty(), label='CheckMainIsEmpty')
            assert_that(results.dead_letter, _check_dead_letter, label='CheckDeadLetter')


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
