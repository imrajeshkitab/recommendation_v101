import os
import json
import pandas as pd
import sys

def main():
    """
    Script to add tags from JSON files to bytes_rows.csv
    Matches files by linear_identifier and embeds JSON directly in the 'tags' column
    """
    
    # Define paths
    json_folder = 'outputs/script_outputs/tag_extractor_batch-bytes'
    csv_path = 'bytes_rows.csv'
    
    # Check if paths exist
    if not os.path.exists(json_folder):
        print(f"❌ Error: JSON folder not found at: {json_folder}")
        sys.exit(1)
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at: {csv_path}")
        sys.exit(1)
    
    # Load the CSV
    print(f"📂 Loading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Check if linear_identifier column exists
    if 'linear_identifier' not in df.columns:
        print(f"❌ Error: 'linear_identifier' column not found in CSV")
        sys.exit(1)
    
    # Create 'tags' column if it doesn't exist
    if 'tags' not in df.columns:
        print("➕ Creating new 'tags' column")
        df['tags'] = None
    
    # Get all JSON files
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    if not json_files:
        print(f"⚠️  Warning: No JSON files found in {json_folder}")
        sys.exit(0)
    
    print(f"🔍 Found {len(json_files)} JSON files to process\n")
    
    # Process each JSON file
    matched_count = 0
    unmatched_count = 0
    
    for json_file in json_files:
        # Extract filename without extension (e.g., BYT-2.json -> BYT-2)
        linear_id = os.path.splitext(json_file)[0]
        
        # Read JSON file
        json_path = os.path.join(json_folder, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")
            continue
        
        # Find matching row in CSV
        mask = df['linear_identifier'] == linear_id
        
        if mask.any():
            # Convert JSON to string for CSV storage
            tags_json_string = json.dumps(tags_data)
            df.loc[mask, 'tags'] = tags_json_string
            matched_count += 1
            print(f"✅ Matched: {linear_id}")
        else:
            unmatched_count += 1
            print(f"⚠️  No match found for: {linear_id}")
    
    # Save updated CSV
    print(f"\n💾 Saving updated CSV to: {csv_path}")
    df.to_csv(csv_path, index=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Total JSON files processed: {len(json_files)}")
    print(f"✅ Successfully matched:     {matched_count}")
    print(f"⚠️  Unmatched:               {unmatched_count}")
    print("="*60)
    print("\n✨ Done!")

if __name__ == "__main__":
    main()

