"""Configuration for AI prompts."""

AI_PROMPT = """Analyze the following issue report from a citizen.
---
Description: {text_to_process}
---
1.  Summarize the issue in one sentence.
2.  Classify it into: [Pothole, Water Logging, Broken Streetlight,
    Garbage Dump, Traffic Jam, Public Safety, Other].
3.  If an image is provided, list key objects detected.
Return a JSON object with keys "summary", "category", "image_tags"."""

ICON_PROMPT = """A simple, modern, flat icon representing '{category}'
for a city services app. Minimalist, vector style, on a white background."""
