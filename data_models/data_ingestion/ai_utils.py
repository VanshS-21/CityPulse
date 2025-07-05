"""
Common utility functions for AI processing.
"""

import json
import mimetypes
import logging
from typing import Optional

import requests
from google.api_core import exceptions
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.vision_models import ImageGenerationModel


def create_ai_client(project_id: str, region: str) -> tuple[GenerativeModel, ImageGenerationModel]:
    """Initializes Vertex AI clients."""
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel("gemini-2.0-flash")
    image_gen_model = ImageGenerationModel.from_pretrained("imagegeneration@005")
    return model, image_gen_model

def get_image_data(image_url: str) -> Optional[tuple[bytes, str]]:
    """
    Downloads and validates image data from URL.
    
    Returns:
        tuple of (image_bytes, mime_type) or None if download fails
    """
    try:
        mime_type, _ = mimetypes.guess_type(image_url)
        if not mime_type or not mime_type.startswith('image'):
            logging.warning(
                "Could not determine a valid image mime type for %s. Defaulting to image/png.", 
                image_url
            )
            mime_type = 'image/png'

        headers = {
            'User-Agent': 'CityPulseBot/1.0 (https://github.com/VanshS-21/CityPulse; citypulse-admin@example.com)'
        }
        response = requests.get(image_url, headers=headers, timeout=60)
        response.raise_for_status()
        return response.content, mime_type
    except requests.exceptions.RequestException as e:
        logging.warning("Could not load image from URL %s: %s", image_url, e)
        return None

def parse_ai_response(response) -> Optional[dict]:
    """Parses the JSON response from the AI model."""
    try:
        return json.loads(response.text.strip("```json\n").strip("```"))
    except (json.JSONDecodeError, AttributeError) as e:
        logging.error("Error parsing AI response: %s. Response: %s", e, response.text)
        return None

def generate_icon(
    storage_client,
    bucket_name: str,
    category: str,
    event_id: str
) -> Optional[str]:
    """
    Generates and uploads an icon for the given category.
    
    Returns:
        Public URL of the icon or None if generation fails
    """
    try:
        prompt = (
            f"A simple, modern, flat icon representing '{category.lower()}' "
            f"for a city services app. Minimalist, vector style, on a white background."
        )
        
        # Create a new image generation model instance
        image_gen_model = ImageGenerationModel.from_pretrained("imagegeneration@005")
        images = image_gen_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1"
        )
        
        if images and (image_bytes := images[0]._image_bytes):
            # Get or create the bucket
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(f"icons/{event_id}_icon.png")
            blob.upload_from_string(image_bytes, content_type='image/png')
            blob.make_public()
            return blob.public_url
    except (exceptions.GoogleAPICallError, ValueError) as e:
        logging.error("Error generating/uploading icon for event %s: %s", event_id, e)
    return None

def create_prompt(text: str, image_url: Optional[str] = None) -> list[Part]:
    """
    Creates prompt parts for the AI model.
    
    Args:
        text: The text description to analyze
        image_url: Optional URL of an image to include in analysis
    
    Returns:
        List of Part objects for the AI model
    """
    prompt_parts = []
    prompt_text = (
        f"""Analyze the following issue report from a citizen.
        ---
        Description: {text}
        ---
        1.  Summarize the issue in one sentence.
        2.  Classify it into: [Pothole, Water Logging, Broken Streetlight,
            Garbage Dump, Traffic Jam, Public Safety, Other].
        3.  If an image is provided, list key objects detected.
        Return a JSON object with keys "summary", "category", "image_tags"."""
    )
    prompt_parts.append(Part.from_text(prompt_text))

    if image_url:
        image_data = get_image_data(image_url)
        if image_data:
            image_bytes, mime_type = image_data
            prompt_parts.append(Part.from_data(image_bytes, mime_type=mime_type))
    
    return prompt_parts
