"""Reusable transforms for processing multimedia data in Beam pipelines."""

import io
import logging

import apache_beam as beam
import requests
from google.api_core import exceptions
from google.cloud import storage

from data_models.firestore_models.event import Event


# pylint: disable=abstract-method
class ProcessMultimedia(beam.DoFn):
    """
    A Beam DoFn that processes multimedia files associated with an event.

    This transform downloads a media file from a public URL, uploads it to a
    specified Google Cloud Storage (GCS) bucket, updates the event metadata
    with the new GCS URI, and tracks success and failure metrics.
    """

    def __init__(self, bucket_name: str):
        """
        Initializes the ProcessMultimedia transform.

        Args:
            bucket_name: The name of the GCS bucket to upload media to.
        """
        super().__init__()
        self.bucket_name = bucket_name
        self.storage_client = None
        self.requests_session = None
        self.success_counter = beam.metrics.Metrics.counter(
            "ProcessMultimedia", "successful_uploads"
        )
        self.failure_counter = beam.metrics.Metrics.counter(
            "ProcessMultimedia", "failed_uploads"
        )

    def start_bundle(self):
        """Initializes non-serializable clients for each bundle of elements."""
        if self.storage_client is None:
            self.storage_client = storage.Client()
        if self.requests_session is None:
            self.requests_session = requests.Session()

    def process(self, element: Event, *args, **kwargs):
        """
        Processes a single event, handling its associated media.

        If the event contains a 'media_url' in its metadata, this method will:
        1. Download the media from the URL.
        2. Upload the media to the configured GCS bucket.
        3. Replace 'media_url' with 'media_gcs_uri' in the metadata.
        4. Yield the updated Event object.

        If no 'media_url' is present, the event is yielded unchanged.
        On failure, a record is sent to the 'dead_letter' output.

        Yields:
            - The processed Event object on success.
            - A TaggedOutput to 'dead_letter' on failure.
        """
        if "media_url" not in element.metadata:
            yield element
            return

        media_url = element.metadata["media_url"]
        try:
            response = self.requests_session.get(media_url, stream=True, timeout=60)
            response.raise_for_status()

            file_name = media_url.split("/")[-1]
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"citizen_reports/{element.id}/{file_name}")

            blob.upload_from_file(io.BytesIO(response.content))

            updated_metadata = element.metadata.copy()
            updated_metadata["media_gcs_uri"] = f"gs://{self.bucket_name}/{blob.name}"
            del updated_metadata["media_url"]

            updated_event = element.model_copy(update={"metadata": updated_metadata})
            self.success_counter.inc()
            yield updated_event

        except (
            requests.exceptions.RequestException,
            exceptions.GoogleAPICallError,
        ) as e:
            error_payload = {
                "pipeline_step": "ProcessMultimedia",
                "raw_data": element.model_dump_json(),
                "error_message": str(e),
            }
            logging.error("Failed to process media for event %s: %s", element.id, e)
            self.failure_counter.inc()
            yield beam.pvalue.TaggedOutput("dead_letter", error_payload)
