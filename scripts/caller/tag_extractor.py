import os
import sys
import json
import argparse
import logging

# --- Import the new reusable Gemini caller ---
try:
    import scripts.endpoints.gemini_service as gemini_caller
except ImportError:
    # Handle error if gemini_caller.py isn't in the same directory or python path
    print("Error: 'gemini_caller.py' not found.", file=sys.stderr)
    print("Please make sure 'gemini_caller.py' is in the same directory or in your PYTHONPATH.", file=sys.stderr)
    sys.exit(1)

# --- 1. Define the task-specific JSON schema ---
# This schema is specific to *this* task.
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

def build_extraction_prompt(prompt_text, summary_text):
    """
    Constructs the specific prompt for the tag extraction task.
    This is part of the "application logic".
    """
    return f"""
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

def read_file(file_path):
    """Helper function to read a file and handle errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    """Helper function to write content to a file, creating dirs."""
    try:
        output_dir_path = os.path.dirname(file_path)
        if output_dir_path:
            os.makedirs(output_dir_path, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Successfully saved output to: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving output file {file_path}: {e}")
        return False

def get_output_path(args, summary_file_path):
    """Determines the correct output file path based on args or defaults."""
    if args.output:
        return args.output
    
    # --- Default output logic from original script ---
    # This assumes this script is in the same location as the original
    # (e.g., .../scripts/tagging/run_tag_extraction.py)
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        # Get script name without extension
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        
        # Create folder with script name
        output_dir = os.path.join(project_root, 'test', 'script_outputs', script_name)
        
        # Get input filename without extension
        input_filename = os.path.splitext(os.path.basename(summary_file_path))[0]
        
        # Create output filename: inputfilename_output.txt
        output_filename = f"{input_filename}_output.txt"
        return os.path.join(output_dir, output_filename)
    except Exception as e:
        logging.warning(f"Could not determine default output path: {e}")
        logging.warning("Defaulting to local directory.")
        return f"{os.path.basename(summary_file_path)}_output.txt"


def main():
    """Main function to orchestrate tag extraction."""
    
    # Configure logging for the main application
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- 1. Parse command-line arguments ---
    parser = argparse.ArgumentParser(
        description='Extract tags from a book summary using Gemini API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tag_extraction.py \\
    --prompt ../../utils/prompts.md \\
    --content ../../test/data/summary/0df57221-d0ad-4377-a47c-33f2d4b47aa3.txt

  python run_tag_extraction.py \\
    -p /path/to/prompts.md \\
    -c /path/to/summary.txt \\
    -o /path/to/output.json
        """
    )
    parser.add_argument('-p', '--prompt', required=True, help='Path to the prompt file (e.g., utils/prompts.md)')
    parser.add_argument('-c', '--content', required=True, help='Path to the content/summary file to analyze')
    parser.add_argument('-o', '--output', default=None, help='Path to save the output file (default: test/script_outputs/<script_name>/<input_filename>_output.txt)')
    
    args = parser.parse_args()
    
    # --- 2. Determine Output Path ---
    output_file = get_output_path(args, args.content)
    logging.info(f"Output will be saved to: {output_file}")

    # --- 3. Read input files ---
    logging.info(f"Reading prompt from: {args.prompt}")
    prompt_text = read_file(args.prompt)
    if prompt_text is None:
        return # Error already logged by read_file
    logging.info(f"✓ Prompt loaded ({len(prompt_text)} characters)")
    
    logging.info(f"Reading summary from: {args.content}")
    summary_text = read_file(args.content)
    if summary_text is None:
        return # Error already logged
    logging.info(f"✓ Summary loaded ({len(summary_text)} characters)")

    # --- 4. Build the task-specific prompt ---
    full_prompt = build_extraction_prompt(prompt_text, summary_text)
    
    # --- 5. Call the reusable Gemini function ---
    logging.info("\n" + "="*60)
    logging.info("EXTRACTING TAGS (JSON) WITH GEMINI API")
    logging.info("="*60 + "\n")

    # Use the imported module
    extracted_tags_json = gemini_caller.generate_json_response(
        prompt=full_prompt,
        json_schema=TAG_SCHEMA
        # We can use the default model 'gemini-2.5-flash'
    )
    
    if not extracted_tags_json:
        logging.error("Failed to extract tags. API call returned None.")
        return

    # --- 6. Validate and Save the output ---
    try:
        # Validate that the response is valid JSON
        json.loads(extracted_tags_json)
        logging.info("✓ API response is valid JSON.")
    except json.JSONDecodeError:
        logging.error("Error: The API response was not valid JSON.")
        logging.error(f"Received:\n{extracted_tags_json}")
        return
    
    # Write the raw JSON string to the file
    if write_file(output_file, extracted_tags_json):
        logging.info("\n" + "="*60)
        logging.info("EXTRACTION COMPLETE")
        logging.info("="*60)
        logging.info(f"Output saved to: {output_file}")
        logging.info("\nExtracted Tags (JSON):\n")
        # Print the clean JSON to stdout for visibility
        print(extracted_tags_json)
        logging.info("\n" + "="*60)
    else:
        logging.error("Failed to write output file.")

if __name__ == "__main__":
    main()
