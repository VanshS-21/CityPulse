"""Tests for the AI processing DoFn."""

import unittest
from unittest.mock import MagicMock, patch

import apache_beam as beam
from apache_beam.testing.util import assert_that, equal_to

from data_models.data_ingestion.ai_processing import ProcessWithAI
from data_models.firestore_models.event import (
    Event,
    EventCategory,
    EventSeverity,
    EventStatus,
    Source,
)
from data_models.tests.common import BaseBeamTest


class ProcessWithAITest(BaseBeamTest):
    """Tests for the ProcessWithAI DoFn."""

    @patch("data_models.data_ingestion.ai_processing.vertexai.GenerativeModel")
    @patch("data_models.data_ingestion.ai_processing.storage.Client")
    @patch("data_models.data_ingestion.ai_processing.aiohttp.ClientSession")
    def test_process_with_ai_success(
        self, mock_session, mock_storage_client, mock_generative_model
    ):
        """Tests successful processing of an event with AI."""
        # Mock AI response
        mock_ai_response = MagicMock()
        mock_ai_response.text = '```json\n{"summary": "AI summary", "category": "TRAFFIC", "image_tags": ["tag1", "tag2"]}\n```'
        mock_generative_model.return_value.generate_content_async.return_value = (
            mock_ai_response
        )

        # Mock Event
        event_data = {
            "id": "test-id",
            "title": "Test Event",
            "description": "This is a test event.",
            "location": {"latitude": 0, "longitude": 0},
            "start_time": "2024-01-01T00:00:00Z",
            "category": EventCategory.OTHER,
            "severity": EventSeverity.LOW,
            "source": Source.CITIZEN_REPORT,
            "status": EventStatus.NEW,
            "metadata": {},
        }
        event = Event(**event_data)

        # Expected event
        expected_event = event.model_copy(deep=True)
        expected_event.ai_summary = "AI summary"
        expected_event.ai_category = EventCategory.TRAFFIC
        expected_event.ai_image_tags = ["tag1", "tag2"]

        # Run pipeline
        results = (
            self.pipeline
            | beam.Create([event])
            | "Process with AI" >> beam.ParDo(ProcessWithAI())
        )

        assert_that(results, equal_to([expected_event]))


if __name__ == "__main__":
    unittest.main()
