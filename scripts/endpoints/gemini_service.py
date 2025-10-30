import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from dotenv import load_dotenv
import logging

# Set up logging for the module
# This will use the root logger configuration if set by the main script
logger = logging.getLogger(__name__)

# Load .env file when the module is first imported
load_dotenv()

def _get_api_key():
    """Internal function to fetch the API key."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")
        raise EnvironmentError("API Key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file.")
    return api_key

def generate_json_response(prompt: str, json_schema: dict, model_name: str = 'gemini-2.5-flash'):
    """
    Calls the Gemini API to get a structured JSON response.

    This is a reusable function that can be called for any task
    that requires a JSON output matching a specific schema.

    Args:
        prompt (str): The full, complete prompt to send to the model.
        json_schema (dict): The schema for the expected JSON output.
        model_name (str, optional): The model to use. Defaults to 'gemini-2.5-flash'.

    Returns:
        str: The JSON response string from the API.
        None: If an error occurred.
    """
    try:
        # --- 1. Configure API ---
        # We get the key and configure on each call to ensure
        # the environment is correctly loaded, though genai.configure
        # can often be called just once.
        api_key = _get_api_key()
        genai.configure(api_key=api_key)
        
        # --- 2. Initialize Model ---
        model = genai.GenerativeModel(model_name)
        
        # --- 3. Create Generation Config ---
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=json_schema
        )
        
        # --- 4. Generate Content ---
        logger.info(f"Sending request to Gemini API (model: {model_name}) for JSON response...")
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        logger.info("Response received successfully from Gemini API!")
        return response.text

    except EnvironmentError as e:
        # This catches the API key error
        logger.error(f"Configuration Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating content from Gemini: {e}")
        # Check for prompt feedback if available
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
            logger.error(f"Prompt Feedback: {response.prompt_feedback}")
        return None

if __name__ == "__main__":
    # This block is for testing the module directly
    print("Testing gemini_caller.py...")
    # You could add a simple test call here if needed
    # For example, define a simple schema and prompt
    try:
        _get_api_key()
        print("✓ API key found.")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    print("This file is intended to be imported as a module, not run directly.")
