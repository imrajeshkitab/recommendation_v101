import os
import sys
import json
import logging
import glob
import concurrent.futures

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
        return True
    except Exception as e:
        logging.error(f"Error saving output file {file_path}: {e}")
        return False

def get_output_path(script_name, summary_file_path):
    """Determines the correct output file path based on the new spec."""
    # Get just the filename, e.g., "0df57221-d0ad-4377-a47c-33f2d4b47aa3.txt"
    input_filename = os.path.basename(summary_file_path)
    
    # Construct the new path: outputs/script_outputs/{script_name}/{input_filename.txt}
    return os.path.join('outputs', 'script_outputs', script_name, input_filename)


def process_file(summary_file_path, prompt_text, script_name):
    """
    Worker function to process a single file.
    This function is designed to be run in a thread.
    """
    file_basename = os.path.basename(summary_file_path)
    logging.info(f"[Task Start] Processing: {file_basename}")

    # --- 1. Read summary ---
    summary_text = read_file(summary_file_path)
    if summary_text is None:
        logging.error(f"[Task Fail] Failed to read: {file_basename}")
        return False # Indicate failure

    # --- 2. Build prompt ---
    full_prompt = build_extraction_prompt(prompt_text, summary_text)
    
    # --- 3. Call API ---
    extracted_tags_json = gemini_caller.generate_json_response(
        prompt=full_prompt,
        json_schema=TAG_SCHEMA
        # We can use the default model 'gemini-1.5-flash'
    )
    
    if not extracted_tags_json:
        logging.error(f"[Task Fail] API call returned None for: {file_basename}")
        return False

    # --- 4. Validate JSON ---
    try:
        json.loads(extracted_tags_json)
    except json.JSONDecodeError:
        logging.error(f"[Task Fail] Invalid JSON received from API for: {file_basename}")
        logging.error(f"Received:\n{extracted_tags_json}")
        return False
    
    # --- 5. Write file ---
    output_file = get_output_path(script_name, summary_file_path)
    
    if write_file(output_file, extracted_tags_json):
        logging.info(f"[Task Success] Saved: {output_file}")
        return True
    else:
        logging.error(f"[Task Fail] Failed to write file: {output_file}")
        return False

def main():
    """Main function to orchestrate batch tag extraction."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- 1. Get inputs from user ---
    logging.info("--- Batch Tag Extraction Script ---")
    
    prompt_file_path = input("➡️ Enter the path to the prompt file (e.g., utils/prompts.md): ")
    if not os.path.isfile(prompt_file_path):
        logging.error(f"❌ Error: Prompt file not found at: {prompt_file_path}")
        sys.exit(1)
        
    content_folder_path = input("➡️ Enter the path to the content *folder* (e.g., test/data/summary): ")
    if not os.path.isdir(content_folder_path):
        logging.error(f"❌ Error: Content folder not found at: {content_folder_path}")
        sys.exit(1)

    # --- 2. Read the single prompt file ---
    logging.info(f"Loading prompt from: {prompt_file_path}")
    prompt_text = read_file(prompt_file_path)
    if prompt_text is None:
        sys.exit(1) # Error already logged by read_file
    logging.info(f"✅ Prompt loaded ({len(prompt_text)} characters)")
    
    # --- 3. Find all content files ---
    # Find all .txt files in the specified folder
    content_files = glob.glob(os.path.join(content_folder_path, "*.txt"))
    if not content_files:
        logging.error(f"❌ Error: No .txt files found in: {content_folder_path}")
        sys.exit(1)
        
    logging.info(f"Found {len(content_files)} .txt files to process.")

    # --- 4. Get script name (for output path) ---
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # --- 5. Process files in parallel ---
    MAX_WORKERS = 8
    success_count = 0
    fail_count = 0
    
    logging.info("\n" + "="*60)
    logging.info(f"🚀 STARTING PARALLEL PROCESSING (Max Workers: {MAX_WORKERS})")
    logging.info("="*60 + "\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Create a dictionary to map futures to their file paths for logging
        future_to_file = {
            executor.submit(process_file, file_path, prompt_text, script_name): file_path 
            for file_path in content_files
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()  # result is True (success) or False (failure)
                if result:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as exc:
                logging.error(f"'{os.path.basename(file_path)}' generated an unexpected exception: {exc}")
                fail_count += 1

    # --- 6. Log final summary ---
    logging.info("\n" + "="*60)
    logging.info("🏁 PROCESSING COMPLETE 🏁")
    logging.info("="*60)
    logging.info(f"Total Files:   {len(content_files)}")
    logging.info(f"✅ Successful:    {success_count}")
    logging.info(f"❌ Failed:        {fail_count}")
    logging.info("="*60)

if __name__ == "__main__":
    main()