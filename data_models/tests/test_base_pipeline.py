import unittest
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to, is_empty
from data_models.data_ingestion.base_pipeline import ParseEvent, WriteToFirestore
from data_models.firestore_models.event import Event

class TestBasePipelineDoFns(unittest.TestCase):
    def test_parse_event_dofn(self):
        with TestPipeline() as p:
            input_data = [
                b'{"title": "Test Event", "description": "A test event."}',
                b'{"title": "Another Event", "invalid_field": "some_value"}'
            ]
            
            results = (
                p | beam.Create(input_data)
                  | beam.ParDo(ParseEvent()).with_outputs('dead_letter', main='parsed_events')
            )
            
            assert_that(results.parsed_events, equal_to([
                Event(title='Test Event', description='A test event.')
            ]), label='CheckParsedEvents')
            
            assert_that(results.dead_letter, equal_to([
                {
                    'pipeline_step': 'ParseEvent',
                    'raw_data': '{"title": "Another Event", "invalid_field": "some_value"}',
                    'error_message': "1 validation error for Event\nunknown field 'invalid_field' (type=value_error.extra)"
                }
            ]), label='CheckDeadLetter')

    def test_write_to_firestore_dofn(self):
        with TestPipeline() as p:
            input_events = [
                Event(title='Event to Write')
            ]
            
            with unittest.mock.patch('data_models.services.firestore_service.FirestoreService') as mock_service:
                instance = mock_service.return_value
                instance.add_document.return_value = None

                results = (
                    p | beam.Create(input_events)
                      | beam.ParDo(WriteToFirestore(project_id='test-project'))
                        .with_outputs('dead_letter', main='firestore_events')
                )

                assert_that(results.firestore_events, equal_to(input_events), label='CheckSuccessfulWrites')
                assert_that(results.dead_letter, is_empty(), label='CheckEmptyDeadLetter')

if __name__ == '__main__':
    unittest.main()
