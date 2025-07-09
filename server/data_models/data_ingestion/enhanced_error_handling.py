"""Enhanced error handling and dead letter queue patterns for Apache Beam pipelines."""

import datetime
import json
import logging
import time
from typing import Any, Dict, Optional, Union

import apache_beam as beam
from apache_beam import window
from apache_beam.metrics import Metrics
from apache_beam.pvalue import TaggedOutput
from pydantic import BaseModel, ValidationError


class ErrorMetadata(BaseModel):
    """Metadata for error tracking and analysis."""

    original_data: Union[str, Dict[str, Any]]
    error_message: str
    error_type: str
    error_timestamp: str
    pipeline_name: str
    processing_stage: str
    retry_count: int = 0
    element_id: Optional[str] = None
    correlation_id: Optional[str] = None


class EnhancedDeadLetterHandler(beam.DoFn):
    """Enhanced dead letter queue handler with comprehensive error tracking."""

    def __init__(self, pipeline_name: str, error_table_spec: str):
        self.pipeline_name = pipeline_name
        self.error_table_spec = error_table_spec

        # Metrics for monitoring
        self.error_counter = Metrics.counter(self.__class__, "dead_letter_events")
        self.error_by_type = Metrics.counter(self.__class__, "errors_by_type")
        self.retry_counter = Metrics.counter(self.__class__, "retry_attempts")

    def process(self, element, error_info=None, processing_stage="unknown"):
        """Process failed elements and create detailed error records."""
        try:
            # Extract retry count if available
            retry_count = getattr(element, "retry_count", 0)
            element_id = getattr(element, "id", None)
            correlation_id = getattr(element, "correlation_id", None)

            # Create comprehensive error metadata
            error_metadata = ErrorMetadata(
                original_data=element,
                error_message=str(error_info) if error_info else "Unknown error",
                error_type=type(error_info).__name__ if error_info else "UnknownError",
                error_timestamp=datetime.datetime.utcnow().isoformat(),
                pipeline_name=self.pipeline_name,
                processing_stage=processing_stage,
                retry_count=retry_count,
                element_id=element_id,
                correlation_id=correlation_id,
            )

            # Update metrics
            self.error_counter.inc()
            self.error_by_type.inc()
            if retry_count > 0:
                self.retry_counter.inc()

            # Log error for monitoring
            logging.error(
                f"Dead letter event in {self.pipeline_name}: "
                f"{error_metadata.error_type} at {processing_stage} - "
                f"{error_metadata.error_message}"
            )

            yield error_metadata.dict()

        except Exception as e:
            # Fallback error handling
            logging.error(f"Failed to process dead letter event: {e}")
            yield {
                "original_data": str(element),
                "error_message": f"Dead letter handler failed: {e}",
                "error_type": "DeadLetterHandlerError",
                "error_timestamp": datetime.datetime.utcnow().isoformat(),
                "pipeline_name": self.pipeline_name,
                "processing_stage": "dead_letter_handler",
                "retry_count": 0,
            }


class MetricsCollector(beam.DoFn):
    """Collects comprehensive metrics for pipeline monitoring."""

    def __init__(self, metric_name: str):
        self.metric_name = metric_name
        self.counter = Metrics.counter(self.__class__, f"{metric_name}_processed")
        self.distribution = Metrics.distribution(
            self.__class__, f"{metric_name}_processing_time"
        )
        self.error_counter = Metrics.counter(self.__class__, f"{metric_name}_errors")

    def process(self, element):
        """Process element with comprehensive metrics collection."""
        start_time = time.time()

        try:
            # Process element (override in subclasses)
            result = self.process_element(element)

            # Record success metrics
            self.counter.inc()
            processing_time = (time.time() - start_time) * 1000  # milliseconds
            self.distribution.update(processing_time)

            yield result

        except Exception as e:
            # Record error metrics
            self.error_counter.inc()

            # Add error context to element for dead letter processing
            element_with_error = {
                "original_element": element,
                "error_info": str(e),
                "processing_stage": self.metric_name,
                "retry_count": getattr(element, "retry_count", 0) + 1,
            }

            # Yield to dead letter output
            yield TaggedOutput("dead_letter", element_with_error)

    def process_element(self, element):
        """Override this method in subclasses for specific processing logic."""
        return element


class AdaptiveWindowingStrategy:
    """Implements adaptive windowing based on data volume and patterns."""

    @staticmethod
    def create_adaptive_window(
        data_volume_threshold: int = 1000,
        low_volume_window: int = 120,
        high_volume_window: int = 30,
    ):
        """
        Creates adaptive windows based on data volume.

        Args:
            data_volume_threshold: Threshold for switching window sizes
            low_volume_window: Window size in seconds for low volume
            high_volume_window: Window size in seconds for high volume
        """
        # This would typically be determined by monitoring metrics
        # For now, we'll use a simple heuristic
        return window.FixedWindows(high_volume_window)

    @staticmethod
    def create_session_window(gap_seconds: int = 300):
        """Creates session-based windowing for related events."""
        return window.Sessions(gap_seconds)

    @staticmethod
    def create_sliding_window(window_size: int = 300, period: int = 60):
        """Creates sliding windows for continuous analysis."""
        return window.SlidingWindows(window_size, period)


class BatchedAPIProcessor(beam.DoFn):
    """Processes elements in batches to optimize external API calls."""

    def __init__(self, batch_size: int = 100, max_wait_time: int = 30):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.batch = []
        self.last_batch_time = time.time()

        # Metrics
        self.batch_counter = Metrics.counter(self.__class__, "batches_processed")
        self.element_counter = Metrics.counter(self.__class__, "elements_processed")

    def process(self, element):
        """Accumulate elements and process in batches."""
        self.batch.append(element)
        current_time = time.time()

        # Process batch if size threshold reached or max wait time exceeded
        if (
            len(self.batch) >= self.batch_size
            or current_time - self.last_batch_time >= self.max_wait_time
        ):

            try:
                results = self.process_batch(self.batch)

                # Update metrics
                self.batch_counter.inc()
                self.element_counter.inc(len(self.batch))

                # Yield all results
                for result in results:
                    yield result

            except Exception as e:
                # Handle batch processing errors
                for element in self.batch:
                    yield TaggedOutput(
                        "dead_letter",
                        {
                            "original_element": element,
                            "error_info": f"Batch processing failed: {e}",
                            "processing_stage": "batch_processing",
                        },
                    )

            # Reset batch
            self.batch = []
            self.last_batch_time = current_time

    def process_batch(self, batch):
        """Override this method to implement specific batch processing logic."""
        # Default implementation - just return the batch
        return batch

    def finish_bundle(self):
        """Process any remaining elements in the batch."""
        if self.batch:
            try:
                results = self.process_batch(self.batch)
                for result in results:
                    yield result
            except Exception as e:
                for element in self.batch:
                    yield TaggedOutput(
                        "dead_letter",
                        {
                            "original_element": element,
                            "error_info": f"Final batch processing failed: {e}",
                            "processing_stage": "batch_processing_final",
                        },
                    )
            finally:
                self.batch = []


class RetryableTransform(beam.PTransform):
    """A transform that implements retry logic for failed elements."""

    def __init__(
        self,
        transform_fn,
        max_retries: int = 3,
        retry_delay: int = 5,
        backoff_multiplier: float = 2.0,
    ):
        self.transform_fn = transform_fn
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier

    def expand(self, pcoll):
        """Implement retry logic with exponential backoff."""

        class RetryDoFn(beam.DoFn):
            def __init__(
                self, transform_fn, max_retries, retry_delay, backoff_multiplier
            ):
                self.transform_fn = transform_fn
                self.max_retries = max_retries
                self.retry_delay = retry_delay
                self.backoff_multiplier = backoff_multiplier

                # Metrics
                self.retry_counter = Metrics.counter(self.__class__, "retry_attempts")
                self.success_counter = Metrics.counter(
                    self.__class__, "successful_retries"
                )
                self.failure_counter = Metrics.counter(
                    self.__class__, "failed_after_retries"
                )

            def process(self, element):
                retry_count = getattr(element, "retry_count", 0)

                try:
                    result = self.transform_fn(element)
                    if retry_count > 0:
                        self.success_counter.inc()
                    yield result

                except Exception as e:
                    if retry_count < self.max_retries:
                        # Prepare element for retry
                        retry_element = (
                            dict(element) if isinstance(element, dict) else element
                        )
                        if isinstance(retry_element, dict):
                            retry_element["retry_count"] = retry_count + 1
                            retry_element["last_error"] = str(e)

                        self.retry_counter.inc()

                        # Add delay for retry (in real implementation, this would be handled by the runner)
                        time.sleep(
                            self.retry_delay * (self.backoff_multiplier**retry_count)
                        )

                        yield retry_element
                    else:
                        # Max retries exceeded, send to dead letter
                        self.failure_counter.inc()
                        yield TaggedOutput(
                            "dead_letter",
                            {
                                "original_element": element,
                                "error_info": f"Max retries ({self.max_retries}) exceeded: {e}",
                                "processing_stage": "retry_transform",
                                "retry_count": retry_count,
                            },
                        )

        return pcoll | beam.ParDo(
            RetryDoFn(
                self.transform_fn,
                self.max_retries,
                self.retry_delay,
                self.backoff_multiplier,
            )
        ).with_outputs("dead_letter", main="main")
