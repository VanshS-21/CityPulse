"""
This module contains ParDo transforms for AI processing of events.
"""

import json
import logging
import mimetypes
import asyncio
import aiohttp

import apache_beam as beam
import requests
import vertexai
from google.api_core import exceptions
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.vision_models import ImageGenerationModel

from data_models.core import config, prompt_config

# pylint: disable=abstract-method
class ProcessWithAI(beam.DoFn):
    """A DoFn to process event data with Generative AI for summarization and classification."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.image_gen_model = None
        self.storage_client = None
        self.bucket = None
        self.session = None

    def setup(self):
        """Initializes clients in the worker."""
        vertexai.init(project=config.PROJECT_ID, location=config.GCP_REGION)
        self.model = GenerativeModel("gemini-1.5-flash-001")
        self.image_gen_model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(config.GCS_GENERATED_IMAGES_BUCKET)

    async def start_session(self):
        """Initialize the aiohttp session for async requests."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _get_prompt_parts(self, text_to_process, image_url):
        """Builds the prompt for the generative AI model."""
        prompt_parts = []
        prompt_text = prompt_config.AI_PROMPT.format(text_to_process=text_to_process)
        prompt_parts.append(Part.from_text(prompt_text))

        if image_url:
            try:
                session = await self.start_session()
                mime_type, _ = mimetypes.guess_type(image_url)
                if not mime_type or not mime_type.startswith('image'):
                    logging.warning(
                        ("Could not determine a valid image mime type for %s. "
                         "Defaulting to image/png."), image_url)
                    mime_type = 'image/png'

                headers = {
                    'User-Agent': 'CityPulseBot/1.0 (https://github.com/VanshS-21/CityPulse; citypulse-admin@example.com)'
                }
                response = await session.get(image_url, headers=headers, timeout=60)
                response.raise_for_status()
                prompt_parts.append(Part.from_data(await response.read(), mime_type=mime_type))
            except Exception as e:
                logging.warning("Could not load image from URL %s: %s", image_url, e)
        return prompt_parts

    def _parse_ai_response(self, response):
        """Parses the JSON response from the AI model."""
        try:
            # First try to extract JSON from markdown code block
            if "```json" in response.text:
                json_text = response.text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_text)
            # If that fails, try to parse the entire response as JSON
            return json.loads(response.text)
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            logging.error("Error parsing AI response: %s. Response: %s", e, response.text)
            return {
                "summary": "Unable to generate summary.",
                "category": "Other",
                "image_tags": []
            }

    async def _generate_and_upload_icon(self, category, event_id):
        """Generates an icon and uploads it to GCS."""
        try:
            prompt = prompt_config.ICON_PROMPT.format(category=category.lower())
            images = await self.image_gen_model.generate_images_async(
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

    async def _get_ai_insights(self, text, image_url):
        """Gets AI insights for the given text and image URL."""
        if not text and not image_url:
            return None

        prompt_parts = await self._get_prompt_parts(text, image_url)
        response = await self.model.generate_content_async(prompt_parts)
        return self._parse_ai_response(response)

    async def _handle_icon_generation(self, category, event_id):
        """Handles the generation and upload of an icon for the given category."""
        if category and category != 'Other':
            return await self._generate_and_upload_icon(category, event_id)
        return None

    async def process_element_async(self, element):
        """Processes a single element asynchronously."""
        try:
            text = element.get('description', '')
            image_url = element.get('image_url')

            ai_insights = await self._get_ai_insights(text, image_url)

            if ai_insights:
                element['ai_summary'] = ai_insights.get('summary')
                element['ai_category'] = ai_insights.get('category')
                element['ai_image_tags'] = ai_insights.get('image_tags', [])

                icon_url = await self._handle_icon_generation(
                    ai_insights.get('category'), element.get('event_id', element.get('id', 'unknown'))
                )
                if icon_url:
                    element['ai_generated_image_url'] = icon_url

            return element

        except (AttributeError, json.JSONDecodeError, requests.exceptions.RequestException,
                ValueError, exceptions.GoogleAPICallError) as e:
            logging.error("Error processing element %s with AI: %s", element.get('event_id', element.get('id', 'unknown')), e)
            return beam.pvalue.TaggedOutput('dead_letter', str(element))
        finally:
            await self.close_session()

    def process(self, element):
        """Processes a single element by applying AI-driven analysis."""
        try:
            # Run the async processing function for a single element
            result = asyncio.run(self.process_element_async(element))
            yield result
        except Exception as e:
            logging.error("Failed to process element with AI: %s", e)
            yield beam.pvalue.TaggedOutput('dead_letter', str(element))
