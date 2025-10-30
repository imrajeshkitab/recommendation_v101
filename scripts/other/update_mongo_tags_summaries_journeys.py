import os
import sys
import json
import glob
from pymongo import MongoClient
from uuid import UUID
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from project root
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

def main():
    """
    Update MongoDB collection with tags from JSON files
    Maps JSON filename (UUID) to MongoDB 'id' field (UUID type)
    Processes all files in outputs/script_outputs/tag_extractor_batch-journeys/
    """
    
    print("="*70)
    print("🏷️  BATCH UPDATE: MongoDB journeys Tags")
    print("="*70)
    
    # Get MongoDB connection string
    mongodb_url = os.getenv('MONGODB_URL2')
    if not mongodb_url:
        print("❌ Error: MONGODB_URL2 not found in .env file")
        return
    
    print("\n🔌 Connecting to MongoDB...")
    try:
        client = MongoClient(mongodb_url, uuidRepresentation='standard')
        db = client['kitab-prod-tables']
        collection = db['journeys']
        print("✅ Connected successfully!")
        print(f"📊 Collection: kitab-prod-tables.journeys")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Find all JSON/TXT files in the directory
    json_folder = os.path.join(project_root, "outputs/script_outputs/tag_extractor_batch-journeys")
    
    if not os.path.isdir(json_folder):
        print(f"❌ Error: Directory not found: {json_folder}")
        client.close()
        return
    
    # Get all .json and .txt files
    json_files = glob.glob(os.path.join(json_folder, "*.json"))
    txt_files = glob.glob(os.path.join(json_folder, "*.txt"))
    all_files = json_files + txt_files
    
    if not all_files:
        print(f"❌ Error: No .json or .txt files found in: {json_folder}")
        client.close()
        return
    
    print(f"\n📂 Found {len(all_files)} files to process")
    print(f"   - JSON files: {len(json_files)}")
    print(f"   - TXT files: {len(txt_files)}")
    
    # Confirm before proceeding
    print(f"\n⚠️  This will update {len(all_files)} documents in MongoDB")
    user_input = input("Continue? (yes/no): ")
    if user_input.lower() != 'yes':
        print("❌ Operation cancelled by user")
        client.close()
        return
    
    # Process each file
    print("\n" + "="*70)
    print("🚀 STARTING BATCH UPDATE")
    print("="*70 + "\n")
    
    success_count = 0
    fail_count = 0
    not_found_count = 0
    already_updated_count = 0
    
    for idx, file_path in enumerate(all_files, 1):
        filename = os.path.basename(file_path)
        # Extract UUID from filename (remove extension)
        uuid_str = os.path.splitext(filename)[0]
        
        print(f"[{idx}/{len(all_files)}] Processing: {filename}")
        
        try:
            # Load tags JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                tags_object = json.load(f)
            
            # Convert UUID string to UUID object
            uuid_obj = UUID(uuid_str)
            
            # Find and update document in MongoDB
            result = collection.update_one(
                {'id': uuid_obj},
                {'$set': {'tags': tags_object}}
            )
            
            if result.matched_count > 0:
                if result.modified_count > 0:
                    print(f"   ✅ Updated: {uuid_str}")
                    success_count += 1
                else:
                    # Document found but not modified (tags might be same)
                    print(f"   ℹ️  Already up-to-date: {uuid_str}")
                    already_updated_count += 1
            else:
                print(f"   ⚠️  Not found in MongoDB: {uuid_str}")
                not_found_count += 1
                
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON for {filename}: {e}")
            fail_count += 1
        except ValueError as e:
            print(f"   ❌ Invalid UUID format {uuid_str}: {e}")
            fail_count += 1
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
            fail_count += 1
    
    # Print summary
    print("\n" + "="*70)
    print("📊 UPDATE SUMMARY")
    print("="*70)
    print(f"Total files processed:     {len(all_files)}")
    print(f"✅ Successfully updated:      {success_count}")
    print(f"ℹ️  Already up-to-date:       {already_updated_count}")
    print(f"⚠️  Not found in MongoDB:     {not_found_count}")
    print(f"❌ Failed:                    {fail_count}")
    print("="*70)
    
    total_success = success_count + already_updated_count
    if total_success == len(all_files):
        print("\n🎉 All documents processed successfully!")
    elif total_success > 0:
        print(f"\n✨ Processed {total_success} out of {len(all_files)} documents.")
    else:
        print("\n⚠️  No documents were updated. Please check the data.")
    
    client.close()
    print("\n🔒 MongoDB connection closed.")

if __name__ == "__main__":
    main()

