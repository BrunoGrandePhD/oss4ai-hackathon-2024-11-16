import base64
import json
import logging
import os

import requests
from langchain_openai import ChatOpenAI

from src.services.llm.prompt_templates import clothing_item

logger = logging.getLogger(__name__)


def analyze_image_with_vision_api(image_path: str) -> str:
    """Analyze image using OpenAI's vision API directly"""
    api_key = os.getenv("OPENAI_API_KEY")

    # Read and encode the image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                            Analyze this clothing item and provide a response in this
                            exact JSON format:

                            {json.dumps(clothing_item, indent=4)}
                        """,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 500,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()

        # Log the raw response for debugging
        logger.info(f"Raw API response: {response.text}")

        response_json = response.json()
        if "choices" not in response_json or not response_json["choices"]:
            raise ValueError("No choices in response")

        content = response_json["choices"][0]["message"]["content"]
        logger.info(f"Response content: {content}")

        # Try to extract JSON from the response
        # First, try to find JSON-like structure
        import re

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)

        # If no JSON found, create a structured response
        logger.warning("No JSON found in response, creating structured response")
        result = {k: "unknown" for k in clothing_item.keys()}
        result["description"] = content
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def process_clothing_image(image_path: str) -> dict:
    """Process a clothing image and classify it."""
    try:
        # Get structured analysis directly from vision API
        result = analyze_image_with_vision_api(image_path)

        # Ensure all required fields are present
        required_fields = clothing_item.keys()
        for field in required_fields:
            if field not in result:
                result[field] = "Not specified"

        return result

    except Exception as e:
        logger.error(f"Error processing clothing image: {str(e)}")
        # Return a structured error response instead of raising
        result = {k: "unknown" for k in clothing_item.keys()}
        result["description"] = f"Error processing image: {str(e)}"
        return result
