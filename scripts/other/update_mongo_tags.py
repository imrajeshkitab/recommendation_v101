import os
import json
import pandas as pd
from pymongo import MongoClient
from uuid import UUID
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Update MongoDB collection with tags from bytes_rows.csv
    Maps CSV 'id' to MongoDB 'id' (UUID) and adds 'tags' field (object type)
    """
    
    # Get MongoDB connection string
    mongodb_url = os.getenv('MONGODB_URL2')
    if not mongodb_url:
        print("❌ Error: MONGODB_URL2 not found in .env file")
        return
    
    print("🔌 Connecting to MongoDB...")
    try:
        client = MongoClient(mongodb_url, uuidRepresentation='standard')
        db = client['kitab-prod-tables']
        collection = db['bytes']
        print("✅ Connected successfully!")
        print(f"📊 Collection: kitab-prod-tables.bytes")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Load CSV
    print("\n📂 Loading bytes_rows.csv...")
    try:
        df = pd.read_csv('bytes_rows.csv')
        print(f"✅ Loaded {len(df)} rows from CSV")
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        client.close()
        return
    
    # Check required columns
    if 'id' not in df.columns or 'tags' not in df.columns:
        print("❌ Error: Required columns 'id' or 'tags' not found in CSV")
        client.close()
        return
    
    # Filter rows that have tags
    rows_with_tags = df[df['tags'].notna()]
    print(f"🏷️  Found {len(rows_with_tags)} rows with tags to update\n")
    
    if len(rows_with_tags) == 0:
        print("⚠️  No tags to update. Exiting.")
        client.close()
        return
    
    # Process each row
    print("🚀 Starting update process...\n")
    
    success_count = 0
    fail_count = 0
    not_found_count = 0
    
    for idx, row in rows_with_tags.iterrows():
        csv_id = row['id']
        tags_json_string = row['tags']
        linear_id = row.get('linear_identifier', 'N/A')
        
        try:
            # Parse tags JSON string to object
            tags_object = json.loads(tags_json_string)
            
            # Convert CSV id string to UUID
            uuid_obj = UUID(csv_id)
            
            # Find and update document in MongoDB
            result = collection.update_one(
                {'id': uuid_obj},
                {'$set': {'tags': tags_object}}
            )
            
            if result.matched_count > 0:
                if result.modified_count > 0:
                    print(f"✅ Updated: {linear_id} (id: {csv_id})")
                    success_count += 1
                else:
                    # Document found but not modified (tags might be same)
                    print(f"ℹ️  Already up-to-date: {linear_id}")
                    success_count += 1
            else:
                print(f"⚠️  Not found in MongoDB: {linear_id} (id: {csv_id})")
                not_found_count += 1
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON for {linear_id}: {e}")
            fail_count += 1
        except Exception as e:
            print(f"❌ Error updating {linear_id}: {e}")
            fail_count += 1
    
    # Print summary
    print("\n" + "="*60)
    print("📊 UPDATE SUMMARY")
    print("="*60)
    print(f"Total rows with tags: {len(rows_with_tags)}")
    print(f"✅ Successfully updated: {success_count}")
    print(f"⚠️  Not found in MongoDB: {not_found_count}")
    print(f"❌ Failed: {fail_count}")
    print("="*60)
    
    if success_count == len(rows_with_tags):
        print("\n🎉 All documents updated successfully!")
    elif success_count > 0:
        print(f"\n✨ Updated {success_count} out of {len(rows_with_tags)} documents.")
    else:
        print("\n⚠️  No documents were updated. Please check the data.")
    
    client.close()
    print("\n🔒 MongoDB connection closed.")

if __name__ == "__main__":
    main()

