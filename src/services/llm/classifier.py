import os
import logging
from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import base64
import requests
import json

logger = logging.getLogger(__name__)

class LLMHandler:
    _instance = None
    _llm = None

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OpenAI API key not found in environment variables")
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            cls._llm = ChatOpenAI(
                model_name="gpt-4",
                api_key=api_key,
                temperature=0.7,
            )
        return cls._llm

def analyze_image_with_vision_api(image_path: str) -> str:
    """Analyze image using OpenAI's vision API directly"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",  # Using standard GPT-4 for now
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this clothing item and provide a response in this exact JSON format:
                        {
                            "category": "type of clothing",
                            "color": "primary colors",
                            "style": "style classification",
                            "pattern": "pattern description",
                            "season": "appropriate seasons",
                            "occasion": "suitable occasions",
                            "description": "detailed description"
                        }"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        
        # Log the raw response for debugging
        logger.info(f"Raw API response: {response.text}")
        
        response_json = response.json()
        if 'choices' not in response_json or not response_json['choices']:
            raise ValueError("No choices in response")
            
        content = response_json['choices'][0]['message']['content']
        logger.info(f"Response content: {content}")
        
        # Try to extract JSON from the response
        # First, try to find JSON-like structure
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
            
        # If no JSON found, create a structured response
        logger.warning("No JSON found in response, creating structured response")
        return {
            "category": "unknown",
            "color": "unknown",
            "style": "unknown",
            "pattern": "unknown",
            "season": "unknown",
            "occasion": "unknown",
            "description": content
        }
        
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
        required_fields = ["category", "color", "style", "pattern", "season", "occasion", "description"]
        for field in required_fields:
            if field not in result:
                result[field] = "Not specified"
                
        return result
        
    except Exception as e:
        logger.error(f"Error processing clothing image: {str(e)}")
        # Return a structured error response instead of raising
        return {
            "error": str(e),
            "category": "error",
            "color": "unknown",
            "style": "unknown",
            "pattern": "unknown",
            "season": "unknown",
            "occasion": "unknown",
            "description": f"Error processing image: {str(e)}"
        }