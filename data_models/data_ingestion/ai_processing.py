"""
This module contains ParDo transforms for AI processing of events.
"""

import json
import logging
import mimetypes

import apache_beam as beam
import requests
import vertexai
from google.api_core import exceptions
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.vision_models import ImageGenerationModel

from data_models.core import config

# pylint: disable=abstract-method
class ProcessWithAI(beam.DoFn):
    """A DoFn to process event data with Generative AI for summarization and classification."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.image_gen_model = None
        self.storage_client = None
        self.bucket = None

    def setup(self):
        """Initializes clients in the worker."""
        vertexai.init(project=config.PROJECT_ID, location=config.GCP_REGION)
        self.model = GenerativeModel("gemini-2.0-flash")
        self.image_gen_model = ImageGenerationModel.from_pretrained("imagegeneration@005")
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(config.GCS_GENERATED_IMAGES_BUCKET)

    def _get_prompt_parts(self, text_to_process, image_url):
        """Builds the prompt for the generative AI model."""
        prompt_parts = []
        prompt_text = (
            f"""Analyze the following issue report from a citizen.
            ---
            Description: {text_to_process}
            ---
            1.  Summarize the issue in one sentence.
            2.  Classify it into: [Pothole, Water Logging, Broken Streetlight,
                Garbage Dump, Traffic Jam, Public Safety, Other].
            3.  If an image is provided, list key objects detected.
            Return a JSON object with keys "summary", "category", "image_tags"."""
        )
        prompt_parts.append(Part.from_text(prompt_text))

        if image_url:
            try:
                mime_type, _ = mimetypes.guess_type(image_url)
                if not mime_type or not mime_type.startswith('image'):
                    logging.warning(
                        ("Could not determine a valid image mime type for %s. "
                         "Defaulting to image/png."), image_url)
                    mime_type = 'image/png'

                headers = {
                    'User-Agent': 'CityPulseBot/1.0 (https://github.com/VanshS-21/CityPulse; citypulse-admin@example.com)'
                }
                response = requests.get(image_url, headers=headers, timeout=60)
                response.raise_for_status()
                prompt_parts.append(Part.from_data(response.content, mime_type=mime_type))
            except requests.exceptions.RequestException as e:
                logging.warning("Could not load image from URL %s: %s", image_url, e)
        return prompt_parts

    def _parse_ai_response(self, response):
        """Parses the JSON response from the AI model."""
        try:
            return json.loads(response.text.strip("```json\n").strip("```"))
        except (json.JSONDecodeError, AttributeError) as e:
            logging.error("Error parsing AI response: %s. Response: %s", e, response.text)
            return None

    def _generate_and_upload_icon(self, category, event_id):
        """Generates an icon and uploads it to GCS."""
        try:
            prompt = (
                f"A simple, modern, flat icon representing '{category.lower()}' "
                f"for a city services app. Minimalist, vector style, on a white background."
            )
            images = self.image_gen_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1")
            if images and (image_bytes := images[0]._image_bytes):  # pylint: disable=protected-access
                blob = self.bucket.blob(f"icons/{event_id}_icon.png")
                blob.upload_from_string(image_bytes, content_type='image/png')
                blob.make_public()
                return blob.public_url
        except (exceptions.GoogleAPICallError, ValueError) as e:
            logging.error("Error generating/uploading icon for event %s: %s", event_id, e)
        return None

    def process(self, element, *args, **kwargs):
        try:
            text = element.get('description', '')
            image_url = element.get('image_url')

            if not text and not image_url:
                yield element
                return

            prompt_parts = self._get_prompt_parts(text, image_url)
            response = self.model.generate_content(prompt_parts)
            ai_insights = self._parse_ai_response(response)

            if ai_insights:
                element['ai_summary'] = ai_insights.get('summary')
                element['ai_category'] = ai_insights.get('category')
                element['ai_image_tags'] = ai_insights.get('image_tags', [])

                category = ai_insights.get('category')
                if category and category != 'Other':
                    icon_url = self._generate_and_upload_icon(category, element['event_id'])
                    if icon_url:
                        element['ai_generated_image_url'] = icon_url

            yield element

        except (AttributeError, json.JSONDecodeError, requests.exceptions.RequestException,
                ValueError, exceptions.GoogleAPICallError) as e:
            logging.error("Error processing element %s with AI: %s", element.get('event_id'), e)
            yield beam.pvalue.TaggedOutput('dead_letter', str(element))
