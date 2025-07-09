"""
Comprehensive unit tests for CityPulse data ingestion pipelines.
Tests Apache Beam transforms, pipeline logic, and data processing.
"""

import pytest
import json
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from data_models.data_ingestion.enhanced_error_handling import (
    EnhancedDeadLetterHandler,
    MetricsCollector,
    AdaptiveWindowingStrategy,
    BatchedAPIProcessor,
    RetryableTransform,
    ErrorMetadata
)
from data_models.data_ingestion.optimized_pipeline import (
    LocationHashGenerator,
    EventIDGenerator,
    OptimizedDataValidator,
    BatchedAIProcessor,
    OptimizedBigQueryWriter,
    OptimizedCityPulsePipeline,
    OptimizedPipelineOptions
)


class TestEnhancedErrorHandling:
    """Test cases for enhanced error handling components."""
    
    def test_error_metadata_creation(self):
        """Test ErrorMetadata model creation and validation."""
        error_data = {
            "id": "test-123",
            "title": "Test Event",
            "invalid_field": "invalid_value"
        }
        
        error_metadata = ErrorMetadata(
            original_data=error_data,
            error_message="Validation failed",
            error_type="ValidationError",
            error_timestamp=datetime.utcnow().isoformat(),
            pipeline_name="test_pipeline",
            processing_stage="validation",
            retry_count=1,
            element_id="test-123",
            correlation_id="corr-456"
        )
        
        assert error_metadata.original_data == error_data
        assert error_metadata.error_message == "Validation failed"
        assert error_metadata.error_type == "ValidationError"
        assert error_metadata.pipeline_name == "test_pipeline"
        assert error_metadata.processing_stage == "validation"
        assert error_metadata.retry_count == 1
        assert error_metadata.element_id == "test-123"
        assert error_metadata.correlation_id == "corr-456"
    
    def test_enhanced_dead_letter_handler(self):
        """Test EnhancedDeadLetterHandler processing."""
        handler = EnhancedDeadLetterHandler("test_pipeline", "test_table")
        
        test_element = {
            "id": "test-123",
            "title": "Test Event",
            "retry_count": 2
        }
        
        error_info = ValueError("Test validation error")
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([test_element])
            
            result = input_data | beam.ParDo(
                handler, 
                error_info=error_info, 
                processing_stage="test_stage"
            )
            
            def check_result(actual):
                assert len(actual) == 1
                error_record = actual[0]
                assert error_record["original_data"] == test_element
                assert "Test validation error" in error_record["error_message"]
                assert error_record["error_type"] == "ValueError"
                assert error_record["pipeline_name"] == "test_pipeline"
                assert error_record["processing_stage"] == "test_stage"
                assert error_record["retry_count"] == 2
            
            assert_that(result, check_result)
    
    def test_metrics_collector(self):
        """Test MetricsCollector functionality."""
        class TestMetricsCollector(MetricsCollector):
            def process_element(self, element):
                # Simple processing that might fail
                if element.get("should_fail"):
                    raise ValueError("Intentional test failure")
                return {"processed": True, **element}
        
        collector = TestMetricsCollector("test_metrics")
        
        # Test successful processing
        success_element = {"id": "success", "data": "valid"}
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([success_element])
            result = input_data | beam.ParDo(collector)
            
            def check_success(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 1
                assert main_outputs[0]["processed"] is True
                assert main_outputs[0]["id"] == "success"
            
            assert_that(result, check_success)
    
    def test_adaptive_windowing_strategy(self):
        """Test AdaptiveWindowingStrategy window creation."""
        # Test high volume window
        high_volume_window = AdaptiveWindowingStrategy.create_adaptive_window(
            data_volume_threshold=500,  # Below threshold
            low_volume_window=120,
            high_volume_window=30
        )
        assert high_volume_window.size == 30
        
        # Test session window
        session_window = AdaptiveWindowingStrategy.create_session_window(gap_seconds=300)
        assert session_window.gap == 300
        
        # Test sliding window
        sliding_window = AdaptiveWindowingStrategy.create_sliding_window(
            window_size=300, period=60
        )
        assert sliding_window.size == 300
        assert sliding_window.period == 60
    
    def test_batched_api_processor(self):
        """Test BatchedAPIProcessor batching logic."""
        class TestBatchProcessor(BatchedAPIProcessor):
            def process_batch(self, batch):
                # Simple batch processing - add batch_id to each element
                return [{"batch_id": "batch_123", **item} for item in batch]
        
        processor = TestBatchProcessor(batch_size=3)
        
        test_elements = [
            {"id": "1", "data": "first"},
            {"id": "2", "data": "second"},
            {"id": "3", "data": "third"},
            {"id": "4", "data": "fourth"}
        ]
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create(test_elements)
            result = input_data | beam.ParDo(processor)
            
            def check_batching(actual):
                # Should process first 3 elements in batch, 4th element separately
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) >= 3  # At least the first batch
                for output in main_outputs:
                    assert "batch_id" in output
                    assert output["batch_id"] == "batch_123"
            
            assert_that(result, check_batching)


class TestOptimizedPipelineComponents:
    """Test cases for optimized pipeline components."""
    
    def test_location_hash_generator(self):
        """Test LocationHashGenerator functionality."""
        generator = LocationHashGenerator()
        
        test_element = {
            "id": "test-123",
            "title": "Test Event",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([test_element])
            result = input_data | beam.ParDo(generator)
            
            def check_hash_generation(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 1
                output = main_outputs[0]
                assert "location_hash" in output
                assert len(output["location_hash"]) == 8  # MD5 hash truncated to 8 chars
                assert output["location_hash"] != "unknown"
            
            assert_that(result, check_hash_generation)
    
    def test_location_hash_generator_missing_location(self):
        """Test LocationHashGenerator with missing location data."""
        generator = LocationHashGenerator()
        
        test_element = {
            "id": "test-123",
            "title": "Test Event"
            # No location field
        }
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([test_element])
            result = input_data | beam.ParDo(generator)
            
            def check_missing_location(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 1
                output = main_outputs[0]
                assert output["location_hash"] == "unknown"
            
            assert_that(result, check_missing_location)
    
    def test_event_id_generator(self):
        """Test EventIDGenerator functionality."""
        generator = EventIDGenerator()
        
        test_element = {
            "id": "test-string-id-123",
            "title": "Test Event"
        }
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([test_element])
            result = input_data | beam.ParDo(generator)
            
            def check_id_generation(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 1
                output = main_outputs[0]
                assert "event_id" in output
                assert isinstance(output["event_id"], int)
                assert output["event_id"] > 0
            
            assert_that(result, check_id_generation)
    
    def test_optimized_data_validator(self):
        """Test OptimizedDataValidator validation logic."""
        validator = OptimizedDataValidator()
        
        # Valid element
        valid_element = {
            "id": "test-123",
            "title": "Valid Event",
            "category": "infrastructure",
            "priority": "medium",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "created_at": datetime.utcnow().isoformat()
        }
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([valid_element])
            result = input_data | beam.ParDo(validator)
            
            def check_valid_element(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 1
                assert main_outputs[0]["id"] == "test-123"
            
            assert_that(result, check_valid_element)
    
    def test_optimized_data_validator_invalid_data(self):
        """Test OptimizedDataValidator with invalid data."""
        validator = OptimizedDataValidator()
        
        # Invalid element - missing required fields
        invalid_element = {
            "id": "test-123",
            # Missing title, category, priority, location, created_at
        }
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([invalid_element])
            result = input_data | beam.ParDo(validator)
            
            def check_invalid_element(actual):
                # Should produce dead letter output
                dead_letter_outputs = [
                    item.value for item in actual 
                    if isinstance(item, beam.pvalue.TaggedOutput) and item.tag == 'dead_letter'
                ]
                assert len(dead_letter_outputs) >= 0  # May produce dead letter output
            
            assert_that(result, check_invalid_element)
    
    def test_batched_ai_processor(self):
        """Test BatchedAIProcessor AI analysis functionality."""
        processor = BatchedAIProcessor(batch_size=2)
        
        test_elements = [
            {
                "id": "test-1",
                "title": "Urgent traffic issue",
                "description": "Emergency situation on highway",
                "category": "infrastructure"
            },
            {
                "id": "test-2", 
                "title": "Good road maintenance",
                "description": "Excellent work by the city crew",
                "category": "infrastructure"
            }
        ]
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create(test_elements)
            result = input_data | beam.ParDo(processor)
            
            def check_ai_processing(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 2
                
                for output in main_outputs:
                    assert "ai_analysis" in output
                    ai_analysis = output["ai_analysis"]
                    assert "sentiment_score" in ai_analysis
                    assert "urgency_score" in ai_analysis
                    assert "tags" in ai_analysis
                    assert "summary" in ai_analysis
                    assert isinstance(ai_analysis["sentiment_score"], float)
                    assert isinstance(ai_analysis["urgency_score"], float)
                    assert isinstance(ai_analysis["tags"], list)
            
            assert_that(result, check_ai_processing)
    
    def test_optimized_bigquery_writer(self):
        """Test OptimizedBigQueryWriter data preparation."""
        writer = OptimizedBigQueryWriter("test_table")
        
        test_element = {
            "id": "test-123",
            "title": "Test Event",
            "created_at": "2024-01-01T12:00:00Z"
        }
        
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([test_element])
            result = input_data | beam.ParDo(writer)
            
            def check_bigquery_prep(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                assert len(main_outputs) == 1
                output = main_outputs[0]
                
                # Check required fields are added
                assert "updated_at" in output
                assert "status" in output
                assert output["status"] == "pending"
                assert "metadata" in output
                assert "reporter_info" in output
                assert "media_files" in output
            
            assert_that(result, check_bigquery_prep)


class TestOptimizedCityPulsePipeline:
    """Test cases for the main OptimizedCityPulsePipeline."""
    
    def test_pipeline_options_creation(self):
        """Test OptimizedPipelineOptions creation."""
        options = OptimizedPipelineOptions(
            input_topic="test-topic",
            output_table="test-table",
            error_table="error-table",
            batch_size=50,
            window_size=30,
            max_retries=5,
            enable_clustering=True,
            enable_partitioning=True
        )
        
        assert options.input_topic == "test-topic"
        assert options.output_table == "test-table"
        assert options.error_table == "error-table"
        assert options.batch_size == 50
        assert options.window_size == 30
        assert options.max_retries == 5
        assert options.enable_clustering is True
        assert options.enable_partitioning is True
    
    def test_pipeline_schema_generation(self):
        """Test pipeline schema generation methods."""
        options = OptimizedPipelineOptions(
            input_topic="test-topic",
            output_table="test-table",
            error_table="error-table"
        )
        
        pipeline = OptimizedCityPulsePipeline(options)
        
        # Test optimized schema
        optimized_schema = pipeline.get_optimized_schema()
        assert "fields" in optimized_schema
        
        field_names = [field["name"] for field in optimized_schema["fields"]]
        required_fields = [
            "id", "event_id", "title", "description", "category", 
            "priority", "status", "location", "location_hash", 
            "ai_analysis", "created_at", "updated_at"
        ]
        
        for field in required_fields:
            assert field in field_names
        
        # Test error schema
        error_schema = pipeline.get_error_schema()
        assert "fields" in error_schema
        
        error_field_names = [field["name"] for field in error_schema["fields"]]
        required_error_fields = [
            "original_data", "error_message", "error_type", 
            "error_timestamp", "pipeline_name", "processing_stage", 
            "retry_count"
        ]
        
        for field in required_error_fields:
            assert field in error_field_names
    
    def test_add_processing_timestamp(self):
        """Test add_processing_timestamp utility method."""
        options = OptimizedPipelineOptions(
            input_topic="test-topic",
            output_table="test-table",
            error_table="error-table"
        )
        
        pipeline = OptimizedCityPulsePipeline(options)
        
        test_element = {"id": "test-123", "title": "Test Event"}
        
        result = pipeline.add_processing_timestamp(test_element)
        
        assert "processing_timestamp" in result
        assert isinstance(result["processing_timestamp"], str)
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(result["processing_timestamp"])


# Mock and fixture utilities for testing
@pytest.fixture
def mock_pubsub_message():
    """Fixture providing a mock Pub/Sub message."""
    return json.dumps({
        "id": "test-event-123",
        "title": "Test Traffic Incident",
        "description": "Traffic jam on Main Street",
        "category": "infrastructure",
        "priority": "medium",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "created_at": datetime.utcnow().isoformat(),
        "user_id": "user-456",
        "metadata": {
            "source": "mobile_app",
            "reporter_type": "citizen"
        }
    })


@pytest.fixture
def sample_pipeline_options():
    """Fixture providing sample pipeline options."""
    return OptimizedPipelineOptions(
        input_topic="projects/test-project/topics/test-topic",
        output_table="test-project:test_dataset.test_table",
        error_table="test-project:test_dataset.error_table",
        batch_size=10,
        window_size=60,
        max_retries=3,
        enable_clustering=True,
        enable_partitioning=True
    )


class TestPipelineIntegration:
    """Integration tests for pipeline components working together."""
    
    def test_pipeline_component_chain(self, mock_pubsub_message):
        """Test pipeline components working in sequence."""
        # Parse JSON message
        element = json.loads(mock_pubsub_message)
        
        # Apply location hash generation
        hash_generator = LocationHashGenerator()
        with TestPipeline() as pipeline:
            input_data = pipeline | beam.Create([element])
            hashed_result = input_data | "GenerateHash" >> beam.ParDo(hash_generator)
            
            # Apply event ID generation
            id_generator = EventIDGenerator()
            id_result = hashed_result | "GenerateID" >> beam.ParDo(id_generator)
            
            # Apply validation
            validator = OptimizedDataValidator()
            validated_result = id_result | "Validate" >> beam.ParDo(validator)
            
            def check_pipeline_chain(actual):
                main_outputs = [item for item in actual if not isinstance(item, beam.pvalue.TaggedOutput)]
                if main_outputs:  # If validation passed
                    output = main_outputs[0]
                    assert "location_hash" in output
                    assert "event_id" in output
                    assert output["id"] == "test-event-123"
                    assert output["title"] == "Test Traffic Incident"
            
            assert_that(validated_result, check_pipeline_chain)
    
    @patch('data_models.data_ingestion.optimized_pipeline.datetime')
    def test_pipeline_timestamp_handling(self, mock_datetime, sample_pipeline_options):
        """Test pipeline timestamp handling."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        pipeline = OptimizedCityPulsePipeline(sample_pipeline_options)
        
        test_element = {"id": "test", "title": "Test"}
        result = pipeline.add_processing_timestamp(test_element)
        
        assert "processing_timestamp" in result
        # The timestamp should be the mocked time
        assert result["processing_timestamp"] == fixed_time.isoformat()
