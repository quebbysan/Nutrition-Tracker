"""
AI meal analysis using the Anthropic API. Reads a text description or a
food photo and returns estimated calories, macros, micronutrients, and
the individual food items (for health-score matching).

SETUP REQUIRED — this does not work until you:
  1. pip install anthropic
  2. Get an API key from https://console.anthropic.com
  3. Set it as an environment variable named ANTHROPIC_API_KEY, OR
     create a file .streamlit/secrets.toml in your repo with:
         ANTHROPIC_API_KEY = "sk-ant-..."
     (add .streamlit/secrets.toml to your .gitignore — never commit a
     real API key to GitHub)

Each analysis call costs a small amount (a fraction of a cent to a few
cents) on your Anthropic account — there's no free local AI here, this
calls Anthropic's servers.
"""

import os
import json
import base64

import streamlit as st
from anthropic import Anthropic

from nutrients_data import NUTRIENT_LOOKUP

MODEL = "claude-sonnet-4-6"


def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            api_key = None
    if not api_key:
        raise RuntimeError(
            "No ANTHROPIC_API_KEY found. Set it as an environment variable "
            "or in .streamlit/secrets.toml before using AI meal analysis."
        )
    return Anthropic(api_key=api_key)


def _build_prompt(description):
    nutrient_list = ", ".join(
        f"{key} ({unit})" for key, (label, unit) in NUTRIENT_LOOKUP.items()
    )
    return f"""You are a nutrition-estimation assistant for a food logging app.
Estimate values as best you can from general nutrition knowledge. Respond
with ONLY valid JSON, no other text, no markdown fences, in this exact shape:

{{
  "meal_name": "short name for the meal",
  "calories": number,
  "protein": number (grams),
  "carbs": number (grams),
  "fat": number (grams),
  "food_items": ["individual food 1", "individual food 2"],
  "nutrients": {{"nutrient_key": number, ...}}
}}

"food_items" should list each distinct food/ingredient separately (e.g.
["grilled chicken breast", "white rice", "broccoli"]) so each can be
health-scored individually.

Only include a nutrient_key in "nutrients" if you can make a reasonable
estimate of it. Valid nutrient_key options are: {nutrient_list}

Meal info: {description}
"""


def _parse_response(text):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def analyze_text(description):
    """description: a plain-language meal description, e.g.
    '2 eggs, a slice of toast, and a banana'."""
    client = _get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": _build_prompt(description)}],
    )
    return _parse_response(message.content[0].text)


def analyze_image(image_bytes, mime_type, description=""):
    """image_bytes: raw bytes of an uploaded/captured photo.
    mime_type: e.g. 'image/jpeg' or 'image/png'.
    description: optional extra context typed alongside the photo."""
    client = _get_client()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = _build_prompt(f"Analyze the attached food photo. {description}".strip())
    message = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return _parse_response(message.content[0].text)
