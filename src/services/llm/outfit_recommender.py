import json
import logging
import os
import re

import requests

from src.services.llm.prompt_templates import (
    outfit_recommendations,
    outfit_recommender_system_prompt,
)
from src.utils.storage import ClosetStorage

logger = logging.getLogger(__name__)


def generate_outfit_recommendations(
    closet: ClosetStorage,
    occasion: str = None,
    season: str = None,
    style: str = None,
) -> list[dict]:
    """
    Generate outfit recommendations based on available clothes in the closet.

    Args:
        closet: ClosetStorage instance
        occasion: Optional filter for specific occasions
        season: Optional filter for specific seasons
        style: Optional filter for specific styles

    Returns:
        List of outfit recommendations, each containing item combinations and styling advice
    """
    try:
        # Initialize storage and get all items
        available_items = closet.get_all_items()

        if not available_items:
            return []

        # Create prompt for GPT-4
        prompt = _create_outfit_prompt(available_items, occasion, season, style)

        # Get API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": outfit_recommender_system_prompt,
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1000,
        }

        # Make API request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()

        # Parse response
        result = response.json()
        outfits = _parse_outfit_response(result["choices"][0]["message"]["content"])

        return outfits

    except Exception as e:
        logger.error(f"Error generating outfit recommendations: {e}")
        raise


def _create_outfit_prompt(
    items: list[dict], occasion: str = None, season: str = None, style: str = None
) -> str:
    """Create a formatted prompt for the GPT-4 API"""

    filters = []
    if occasion:
        filters.append(f"occasion: {occasion}")
    if season:
        filters.append(f"season: {season}")
    if style:
        filters.append(f"style: {style}")

    filter_text = (
        f"\nPlease consider these filters: {', '.join(filters)}" if filters else ""
    )

    return f"""Available clothing items in the closet:

{json.dumps(items, indent=2)}

Please create 3-5 outfit combinations using these items.{filter_text}

Respond in the following JSON format:
{json.dumps(outfit_recommendations, indent=2)}
"""


def _parse_outfit_response(response_text: str) -> list[dict]:
    """Parse the GPT response into structured outfit recommendations"""
    try:
        # Find JSON in response
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON found in response")

        recommendations = json.loads(json_match.group())
        if not recommendations.get("outfits"):
            raise ValueError("No outfits found in response")
        return recommendations["outfits"]

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing outfit response: {e}")
        raise ValueError("Invalid response format from GPT")
