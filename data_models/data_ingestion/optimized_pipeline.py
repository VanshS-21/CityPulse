"""
Optimized Apache Beam pipeline implementing 2024-2025 performance best practices.
Includes adaptive windowing, batched processing, and enhanced error handling.
"""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam import window
from apache_beam.metrics import Metrics
from apache_beam.pvalue import TaggedOutput
import json
import logging
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .enhanced_error_handling import (
    EnhancedDeadLetterHandler,
    MetricsCollector,
    AdaptiveWindowingStrategy,
    BatchedAPIProcessor,
    RetryableTransform
)


@dataclass
class OptimizedPipelineOptions:
    """Configuration options for the optimized pipeline."""
    input_topic: str
    output_table: str
    error_table: str
    batch_size: int = 100
    window_size: int = 60
    max_retries: int = 3
    enable_clustering: bool = True
    enable_partitioning: bool = True


class LocationHashGenerator(beam.DoFn):
    """Generates geohash for location clustering optimization."""
    
    def __init__(self):
        self.hash_counter = Metrics.counter(self.__class__, 'location_hashes_generated')
    
    def process(self, element):
        """Generate location hash for clustering."""
        try:
            if 'location' in element and 'latitude' in element['location'] and 'longitude' in element['location']:
                lat = element['location']['latitude']
                lng = element['location']['longitude']
                
                # Generate geohash (simplified version for clustering)
                location_string = f"{lat:.4f},{lng:.4f}"
                location_hash = hashlib.md5(location_string.encode()).hexdigest()[:8]
                
                element['location_hash'] = location_hash
                self.hash_counter.inc()
            else:
                element['location_hash'] = 'unknown'
            
            yield element
            
        except Exception as e:
            yield TaggedOutput('dead_letter', {
                'original_element': element,
                'error_info': f'Location hash generation failed: {e}',
                'processing_stage': 'location_hash_generation'
            })


class EventIDGenerator(beam.DoFn):
    """Generates numeric event IDs for optimized joins."""
    
    def __init__(self):
        self.id_counter = Metrics.counter(self.__class__, 'event_ids_generated')
    
    def process(self, element):
        """Generate numeric event ID from string ID."""
        try:
            if 'id' in element:
                # Generate consistent numeric ID from string ID
                string_id = element['id']
                numeric_id = int(hashlib.md5(string_id.encode()).hexdigest()[:15], 16)
                element['event_id'] = numeric_id
                self.id_counter.inc()
            
            yield element
            
        except Exception as e:
            yield TaggedOutput('dead_letter', {
                'original_element': element,
                'error_info': f'Event ID generation failed: {e}',
                'processing_stage': 'event_id_generation'
            })


class OptimizedDataValidator(MetricsCollector):
    """Enhanced data validator with performance optimizations."""
    
    def __init__(self):
        super().__init__('data_validation')
        self.validation_rules = {
            'required_fields': ['id', 'title', 'category', 'priority', 'location', 'created_at'],
            'valid_categories': ['infrastructure', 'safety', 'environment', 'other'],
            'valid_priorities': ['low', 'medium', 'high', 'critical'],
            'valid_statuses': ['pending', 'in_progress', 'resolved', 'closed']
        }
    
    def process_element(self, element):
        """Validate element with optimized checks."""
        # Early validation - check required fields first
        for field in self.validation_rules['required_fields']:
            if field not in element:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate categorical fields
        if element.get('category') not in self.validation_rules['valid_categories']:
            raise ValueError(f"Invalid category: {element.get('category')}")
        
        if element.get('priority') not in self.validation_rules['valid_priorities']:
            raise ValueError(f"Invalid priority: {element.get('priority')}")
        
        # Validate location structure
        location = element.get('location', {})
        if not isinstance(location, dict):
            raise ValueError("Location must be a dictionary")
        
        if 'latitude' not in location or 'longitude' not in location:
            raise ValueError("Location must contain latitude and longitude")
        
        # Validate coordinate ranges
        lat = location['latitude']
        lng = location['longitude']
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError(f"Invalid coordinates: lat={lat}, lng={lng}")
        
        return element


class BatchedAIProcessor(BatchedAPIProcessor):
    """Batched AI processing for performance optimization."""
    
    def __init__(self, batch_size: int = 50):
        super().__init__(batch_size)
        self.ai_counter = Metrics.counter(self.__class__, 'ai_analyses_completed')
    
    def process_batch(self, batch):
        """Process batch of elements through AI analysis."""
        try:
            # Simulate AI processing (replace with actual AI service calls)
            results = []
            
            for element in batch:
                # Generate AI analysis
                ai_analysis = self.generate_ai_analysis(element)
                element['ai_analysis'] = ai_analysis
                results.append(element)
                self.ai_counter.inc()
            
            return results
            
        except Exception as e:
            logging.error(f"Batch AI processing failed: {e}")
            raise
    
    def generate_ai_analysis(self, element):
        """Generate AI analysis for an element."""
        # Simplified AI analysis (replace with actual AI service)
        text_content = f"{element.get('title', '')} {element.get('description', '')}"
        
        # Simulate sentiment analysis
        sentiment_score = 0.5  # Neutral sentiment as default
        if 'urgent' in text_content.lower() or 'emergency' in text_content.lower():
            sentiment_score = 0.2  # Negative sentiment
            urgency_score = 0.9
        elif 'good' in text_content.lower() or 'excellent' in text_content.lower():
            sentiment_score = 0.8  # Positive sentiment
            urgency_score = 0.3
        else:
            urgency_score = 0.5
        
        # Generate tags based on content
        tags = []
        if element.get('category') == 'infrastructure':
            tags.extend(['infrastructure', 'maintenance'])
        if element.get('priority') == 'critical':
            tags.append('critical')
        
        return {
            'sentiment_score': sentiment_score,
            'urgency_score': urgency_score,
            'tags': tags,
            'summary': f"Auto-generated summary for {element.get('category', 'unknown')} issue"
        }


class OptimizedBigQueryWriter(beam.DoFn):
    """Optimized BigQuery writer with batching and error handling."""
    
    def __init__(self, table_spec: str):
        self.table_spec = table_spec
        self.write_counter = Metrics.counter(self.__class__, 'records_written')
        self.error_counter = Metrics.counter(self.__class__, 'write_errors')
    
    def process(self, element):
        """Process element for BigQuery writing."""
        try:
            # Ensure timestamps are properly formatted
            if 'created_at' in element:
                if isinstance(element['created_at'], str):
                    element['created_at'] = datetime.fromisoformat(element['created_at'].replace('Z', '+00:00'))
            
            if 'updated_at' not in element:
                element['updated_at'] = datetime.utcnow()
            
            # Ensure all required fields are present
            self.ensure_required_fields(element)
            
            self.write_counter.inc()
            yield element
            
        except Exception as e:
            self.error_counter.inc()
            yield TaggedOutput('dead_letter', {
                'original_element': element,
                'error_info': f'BigQuery write preparation failed: {e}',
                'processing_stage': 'bigquery_write_prep'
            })
    
    def ensure_required_fields(self, element):
        """Ensure all required fields are present and properly formatted."""
        # Set default values for optional fields
        if 'status' not in element:
            element['status'] = 'pending'
        
        if 'metadata' not in element:
            element['metadata'] = {}
        
        # Ensure nested structures are properly formatted
        if 'reporter_info' not in element:
            element['reporter_info'] = {}
        
        if 'media_files' not in element:
            element['media_files'] = []


class OptimizedCityPulsePipeline:
    """Main optimized pipeline class implementing performance best practices."""
    
    def __init__(self, options: OptimizedPipelineOptions):
        self.options = options
        self.pipeline_metrics = {
            'total_processed': Metrics.counter('OptimizedPipeline', 'total_elements_processed'),
            'successful_writes': Metrics.counter('OptimizedPipeline', 'successful_writes'),
            'dead_letter_events': Metrics.counter('OptimizedPipeline', 'dead_letter_events')
        }
    
    def create_pipeline(self, pipeline_options: PipelineOptions):
        """Create the optimized Apache Beam pipeline."""
        
        with beam.Pipeline(options=pipeline_options) as pipeline:
            
            # Read from Pub/Sub with adaptive windowing
            raw_events = (
                pipeline
                | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(topic=self.options.input_topic)
                | 'ParseJSON' >> beam.Map(json.loads)
                | 'AddTimestamps' >> beam.Map(self.add_processing_timestamp)
            )
            
            # Apply adaptive windowing strategy
            windowed_events = (
                raw_events
                | 'ApplyWindowing' >> beam.WindowInto(
                    AdaptiveWindowingStrategy.create_adaptive_window(
                        data_volume_threshold=1000,
                        low_volume_window=self.options.window_size * 2,
                        high_volume_window=self.options.window_size
                    )
                )
            )
            
            # Data validation with retry logic
            validated_events = (
                windowed_events
                | 'ValidateData' >> RetryableTransform(
                    OptimizedDataValidator(),
                    max_retries=self.options.max_retries
                )
            )
            
            # Generate optimized IDs and hashes
            enriched_events = (
                validated_events.main
                | 'GenerateEventID' >> beam.ParDo(EventIDGenerator()).with_outputs('dead_letter', main='main')
                | 'GenerateLocationHash' >> beam.ParDo(LocationHashGenerator()).with_outputs('dead_letter', main='main')
            )
            
            # Batched AI processing
            ai_processed_events = (
                enriched_events.main
                | 'BatchedAIProcessing' >> beam.ParDo(BatchedAIProcessor(self.options.batch_size))
                    .with_outputs('dead_letter', main='main')
            )
            
            # Prepare for BigQuery writing
            bigquery_ready = (
                ai_processed_events.main
                | 'PrepareForBigQuery' >> beam.ParDo(OptimizedBigQueryWriter(self.options.output_table))
                    .with_outputs('dead_letter', main='main')
            )
            
            # Write to BigQuery with optimized schema
            (
                bigquery_ready.main
                | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
                    table=self.options.output_table,
                    schema=self.get_optimized_schema(),
                    write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    additional_bq_parameters={
                        'timePartitioning': {
                            'type': 'DAY',
                            'field': 'created_at'
                        },
                        'clustering': {
                            'fields': ['location_hash', 'category', 'priority']
                        } if self.options.enable_clustering else None
                    }
                )
                | 'CountSuccessfulWrites' >> beam.Map(lambda x: self.pipeline_metrics['successful_writes'].inc())
            )
            
            # Collect all dead letter events
            all_dead_letters = (
                (
                    validated_events.dead_letter,
                    enriched_events.dead_letter,
                    ai_processed_events.dead_letter,
                    bigquery_ready.dead_letter
                )
                | 'FlattenDeadLetters' >> beam.Flatten()
                | 'ProcessDeadLetters' >> beam.ParDo(
                    EnhancedDeadLetterHandler('OptimizedCityPulsePipeline', self.options.error_table)
                )
                | 'WriteDeadLetters' >> beam.io.WriteToBigQuery(
                    table=self.options.error_table,
                    schema=self.get_error_schema(),
                    write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                )
                | 'CountDeadLetters' >> beam.Map(lambda x: self.pipeline_metrics['dead_letter_events'].inc())
            )
            
            # Count total processed elements
            (
                raw_events
                | 'CountTotalProcessed' >> beam.Map(lambda x: self.pipeline_metrics['total_processed'].inc())
            )
    
    def add_processing_timestamp(self, element):
        """Add processing timestamp to element."""
        element['processing_timestamp'] = datetime.utcnow().isoformat()
        return element
    
    def get_optimized_schema(self):
        """Get the optimized BigQuery schema."""
        return {
            'fields': [
                {'name': 'id', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'event_id', 'type': 'INTEGER', 'mode': 'REQUIRED'},
                {'name': 'title', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'description', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'category', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'priority', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'status', 'type': 'STRING', 'mode': 'REQUIRED'},
                {
                    'name': 'location',
                    'type': 'RECORD',
                    'mode': 'REQUIRED',
                    'fields': [
                        {'name': 'latitude', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                        {'name': 'longitude', 'type': 'FLOAT', 'mode': 'REQUIRED'},
                        {'name': 'address', 'type': 'STRING', 'mode': 'NULLABLE'},
                        {'name': 'district', 'type': 'STRING', 'mode': 'NULLABLE'}
                    ]
                },
                {'name': 'location_hash', 'type': 'STRING', 'mode': 'REQUIRED'},
                {
                    'name': 'ai_analysis',
                    'type': 'RECORD',
                    'mode': 'NULLABLE',
                    'fields': [
                        {'name': 'sentiment_score', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                        {'name': 'urgency_score', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                        {'name': 'tags', 'type': 'STRING', 'mode': 'REPEATED'},
                        {'name': 'summary', 'type': 'STRING', 'mode': 'NULLABLE'}
                    ]
                },
                {'name': 'created_at', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'updated_at', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'processing_timestamp', 'type': 'TIMESTAMP', 'mode': 'NULLABLE'}
            ]
        }
    
    def get_error_schema(self):
        """Get the error table schema."""
        return {
            'fields': [
                {'name': 'original_data', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'error_message', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'error_type', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'error_timestamp', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'pipeline_name', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'processing_stage', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'retry_count', 'type': 'INTEGER', 'mode': 'REQUIRED'},
                {'name': 'element_id', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'correlation_id', 'type': 'STRING', 'mode': 'NULLABLE'}
            ]
        }


def run_optimized_pipeline(argv=None):
    """Main function to run the optimized pipeline."""
    
    # Parse pipeline options
    pipeline_options = PipelineOptions(argv)
    
    # Configure optimized pipeline options
    optimized_options = OptimizedPipelineOptions(
        input_topic='projects/your-project/topics/citizen-reports',
        output_table='your-project:citypulse_analytics_optimized.events_optimized',
        error_table='your-project:citypulse_analytics_optimized.pipeline_errors',
        batch_size=100,
        window_size=60,
        max_retries=3,
        enable_clustering=True,
        enable_partitioning=True
    )
    
    # Create and run pipeline
    pipeline = OptimizedCityPulsePipeline(optimized_options)
    pipeline.create_pipeline(pipeline_options)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run_optimized_pipeline()
