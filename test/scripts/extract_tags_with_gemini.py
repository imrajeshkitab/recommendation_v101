import os
import sys
import json
import argparse
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- 1. Define the desired output JSON schema ---
# This schema matches the structure you requested.
TAG_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "life_stage_age": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "life_stage_relationship": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "life_stage_parenting": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "primary_need": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "motivation_driver": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "cognitive_style": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "content_depth": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "learning_style": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
    },
    "required": [
        "life_stage_age", "life_stage_relationship", "life_stage_parenting",
        "primary_need", "motivation_driver", "cognitive_style",
        "content_depth", "learning_style"
    ]
}


def extract_tags_from_summary(prompt_text, summary_text):
    """
    Extract tags from a book summary using Gemini API with structured output.
    
    Args:
        prompt_text (str): The instruction prompt (containing tag definitions)
        summary_text (str): The book summary text to analyze
    
    Returns:
        str: A JSON string containing the extracted tags, or None on failure.
    """
    
    # --- 1. Get API Key ---
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please make sure you have a .env file with GEMINI_API_KEY=your_api_key")
        return None
    
    # --- 2. Configure Gemini API ---
    genai.configure(api_key=api_key)
    
    # --- 3. Initialize the model ---
    # Using a model that supports structured JSON output
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # --- 4. Create the Generation Config for JSON output ---
    # This tells the model to ONLY output JSON matching our schema
    generation_config = GenerationConfig(
        response_mime_type="application/json",
        response_schema=TAG_SCHEMA
    )
    
    # --- 5. Create the full prompt ---
    # Simplified to focus on the task, as formatting is handled by the schema.
    full_prompt = f"""
Here are the definitions for the 8 tag categories:

---
{prompt_text}
---

## Book Summary to Analyze:

{summary_text}

---

## Task:
Based *only* on the book summary provided, extract all relevant tags that fit into the 8 categories.
If no tags from a category apply, return an empty array for that category.
Format your response *only* as a JSON object matching the provided schema.
"""
    
    # --- 6. Generate response ---
    print("Sending request to Gemini API (expecting structured JSON)...")
    try:
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        print("Response received successfully!")
        
        # The response text *is* the JSON string
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        # This can happen if the model fails to generate valid JSON
        if hasattr(response, 'prompt_feedback'):
            print(f"Prompt Feedback: {response.prompt_feedback}")
        return None


def main():
    """Main function to orchestrate tag extraction."""
    
    # --- Parse command-line arguments ---
    parser = argparse.ArgumentParser(
        description='Extract tags from a book summary using Gemini API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_tags_with_gemini.py \\
    --prompt ../../utils/prompts.md \\
    --content ../../test/data/summary/0df57221-d0ad-4377-a47c-33f2d4b47aa3.txt

  python extract_tags_with_gemini.py \\
    -p /path/to/prompts.md \\
    -c /path/to/summary.txt \\
    -o /path/to/output.json
        """
    )
    
    parser.add_argument(
        '-p', '--prompt',
        required=True,
        help='Path to the prompt file (e.g., utils/prompts.md)'
    )
    
    parser.add_argument(
        '-c', '--content',
        required=True,
        help='Path to the content/summary file to analyze'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Path to save the output file (default: test/script_outputs/extract_tags_with_gemini/<input_filename>_output.txt)'
    )
    
    args = parser.parse_args()
    
    # Set file paths from arguments
    prompt_file = args.prompt
    summary_file = args.content
    
    # Set output file
    if args.output:
        output_file = args.output
    else:
        # Default output location
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        # Get script name without extension
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        
        # Create folder with script name
        output_dir = os.path.join(project_root, 'test', 'script_outputs', script_name)
        
        # Get input filename without extension
        input_filename = os.path.splitext(os.path.basename(summary_file))[0]
        
        # Create output filename: inputfilename_output.txt
        output_filename = f"{input_filename}_output.txt"
        output_file = os.path.join(output_dir, output_filename)
    
    # --- 1. Read the prompt ---
    print(f"Reading prompt from: {prompt_file}")
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
        print(f"✓ Prompt loaded successfully ({len(prompt_text)} characters)")
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_file}")
        return
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return
    
    # --- 2. Read the book summary ---
    print(f"\nReading book summary from: {summary_file}")
    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_text = f.read()
        print(f"✓ Summary loaded successfully ({len(summary_text)} characters)")
    except FileNotFoundError:
        print(f"Error: Summary file not found at {summary_file}")
        return
    except Exception as e:
        print(f"Error reading summary file: {e}")
        return
    
    # --- 3. Extract tags using Gemini ---
    print("\n" + "="*60)
    print("EXTRACTING TAGS (JSON) WITH GEMINI API")
    print("="*60 + "\n")
    
    extracted_tags_json = extract_tags_from_summary(prompt_text, summary_text)
    
    if not extracted_tags_json:
        print("\nFailed to extract tags.")
        return
    
    # --- 4. Validate and Save the output ---
    print(f"\nSaving JSON output to: {output_file}")
    try:
        # Validate that the response is valid JSON before saving
        json.loads(extracted_tags_json) # This will raise an error if not valid JSON
        
        # Create output directory if it doesn't exist
        output_dir_path = os.path.dirname(output_file)
        if output_dir_path:
            os.makedirs(output_dir_path, exist_ok=True)
        
        # Write only the raw JSON string to the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extracted_tags_json)
        print(f"✓ JSON output saved successfully!")
    except json.JSONDecodeError:
        print("Error: The API response was not valid JSON.")
        print("Received:\n", extracted_tags_json)
    except Exception as e:
        print(f"Error saving output file: {e}")
        return
    
    # --- 5. Display results ---
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print("\nExtracted Tags (JSON):\n")
    print(extracted_tags_json)
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
