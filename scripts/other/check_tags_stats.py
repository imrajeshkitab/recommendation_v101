import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Check statistics for 'tags' field in kitab-prod-tables.bytes_tagged collection
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
        collection = db['bytes_tagged']
        print("✅ Connected successfully!")
        print(f"📊 Collection: kitab-prod-tables.bytes_tagged\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Get total count
    total_count = collection.count_documents({})
    print(f"📈 Total documents in collection: {total_count}")
    
    # Count documents with 'tags' field
    with_tags_count = collection.count_documents({'tags': {'$exists': True}})
    print(f"✅ Documents WITH 'tags' field: {with_tags_count}")
    
    # Count documents without 'tags' field
    without_tags_count = collection.count_documents({'tags': {'$exists': False}})
    print(f"❌ Documents WITHOUT 'tags' field: {without_tags_count}")
    
    # Calculate percentages
    if total_count > 0:
        with_tags_percent = (with_tags_count / total_count) * 100
        without_tags_percent = (without_tags_count / total_count) * 100
        
        print(f"\n📊 Percentage breakdown:")
        print(f"  WITH tags:    {with_tags_percent:.2f}%")
        print(f"  WITHOUT tags: {without_tags_percent:.2f}%")
    
    # Show sample document with tags (if any)
    if with_tags_count > 0:
        print(f"\n🔍 Sample document with tags:")
        sample_doc = collection.find_one({'tags': {'$exists': True}})
        if sample_doc:
            print(f"  _id: {sample_doc.get('_id')}")
            print(f"  id: {sample_doc.get('id')}")
            print(f"  linear_identifier: {sample_doc.get('linear_identifier', 'N/A')}")
            print(f"  tags type: {type(sample_doc.get('tags'))}")
            if isinstance(sample_doc.get('tags'), dict):
                print(f"  tags keys: {list(sample_doc.get('tags').keys())}")
    
    # Show sample document without tags (if any)
    if without_tags_count > 0:
        print(f"\n🔍 Sample document WITHOUT tags:")
        sample_doc = collection.find_one({'tags': {'$exists': False}})
        if sample_doc:
            print(f"  _id: {sample_doc.get('_id')}")
            print(f"  id: {sample_doc.get('id')}")
            print(f"  linear_identifier: {sample_doc.get('linear_identifier', 'N/A')}")
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Total documents:      {total_count}")
    print(f"✅ WITH 'tags':       {with_tags_count} ({with_tags_percent:.2f}%)")
    print(f"❌ WITHOUT 'tags':    {without_tags_count} ({without_tags_percent:.2f}%)")
    print("="*60)
    
    client.close()
    print("\n🔒 MongoDB connection closed.")

if __name__ == "__main__":
    main()

