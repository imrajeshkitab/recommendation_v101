import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Remove documents without 'tags' field from kitab-prod-tables.bytes_tagged collection
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
    
    # Get initial counts
    total_before = collection.count_documents({})
    without_tags_count = collection.count_documents({'tags': {'$exists': False}})
    
    print(f"📈 Current state:")
    print(f"  Total documents: {total_before}")
    print(f"  Documents WITHOUT tags: {without_tags_count}")
    
    if without_tags_count == 0:
        print("\n✨ No documents to delete. All documents have tags!")
        client.close()
        return
    
    # Show sample of what will be deleted
    print(f"\n🔍 Sample of documents to be deleted (first 5):")
    sample_docs = collection.find({'tags': {'$exists': False}}).limit(5)
    for i, doc in enumerate(sample_docs, 1):
        print(f"  {i}. _id: {doc.get('_id')}, id: {doc.get('id')}, linear_id: {doc.get('linear_identifier', 'N/A')}")
    
    # Confirmation
    print(f"\n⚠️  WARNING: This will DELETE {without_tags_count} documents!")
    confirm = input("Are you sure you want to proceed? Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("\n❌ Operation cancelled.")
        client.close()
        return
    
    # Delete documents without tags
    print(f"\n🗑️  Deleting documents without 'tags' field...")
    result = collection.delete_many({'tags': {'$exists': False}})
    
    # Get final count
    total_after = collection.count_documents({})
    
    # Summary
    print("\n" + "="*60)
    print("📊 DELETION SUMMARY")
    print("="*60)
    print(f"Documents before deletion: {total_before}")
    print(f"Documents deleted:         {result.deleted_count}")
    print(f"Documents remaining:       {total_after}")
    print("="*60)
    
    if result.deleted_count == without_tags_count:
        print("\n✅ Successfully deleted all documents without tags!")
    else:
        print(f"\n⚠️  Expected to delete {without_tags_count} but deleted {result.deleted_count}")
    
    # Verify all remaining docs have tags
    remaining_without_tags = collection.count_documents({'tags': {'$exists': False}})
    print(f"\n🔍 Verification: {remaining_without_tags} documents without tags remaining")
    
    if remaining_without_tags == 0:
        print("✨ All remaining documents have the 'tags' field!")
    
    client.close()
    print("\n🔒 MongoDB connection closed.")

if __name__ == "__main__":
    main()

