"""
Add 'published' field to all documents in the 'journeys' collection

This script connects to MongoDB and adds a 'published: True' field to all
documents in the journeys collection that don't already have it.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

def add_published_field():
    """
    Add 'published: True' field to all documents in journeys collection
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get MongoDB URL from environment
    mongodb_url = os.getenv('MONGODB_URL') or os.getenv('MONGODB_URL2')
    
    if not mongodb_url:
        print("❌ ERROR: MONGODB_URL not found in .env file")
        return False
    
    print(f"🔍 Connecting to MongoDB...")
    
    try:
        # Create MongoDB client
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000, uuidRepresentation='standard')
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        
        # Access the database and collection
        db = client['kitab-prod-tables']
        collection = db['journeys']
        
        # Get initial counts
        total_count = collection.count_documents({})
        print(f"\n📊 Total documents in 'journeys' collection: {total_count}")
        
        if total_count == 0:
            print("⚠️  Collection is empty! Nothing to update.")
            client.close()
            return True
        
        # Check current state
        with_published = collection.count_documents({'published': {'$exists': True}})
        without_published = total_count - with_published
        
        print(f"\n📋 Current state:")
        print(f"   • Documents WITH 'published' field: {with_published}")
        print(f"   • Documents WITHOUT 'published' field: {without_published}")
        
        if without_published == 0:
            print("\n✅ All documents already have the 'published' field!")
            client.close()
            return True
        
        # Update documents without 'published' field
        print(f"\n🔧 Adding 'published: true' to {without_published} document(s)...")
        
        result = collection.update_many(
            {'published': {'$exists': False}},  # Only update documents without the field
            {'$set': {'published': True}}        # Set published to True
        )
        
        print(f"✅ Update completed!")
        print(f"   • Matched: {result.matched_count} document(s)")
        print(f"   • Modified: {result.modified_count} document(s)")
        
        # Verify the update
        print("\n🔎 Verifying update...")
        
        updated_with_published = collection.count_documents({'published': {'$exists': True}})
        updated_published_true = collection.count_documents({'published': True})
        updated_published_false = collection.count_documents({'published': False})
        
        print(f"   • Total documents with 'published' field: {updated_with_published}")
        print(f"   • Documents with published = True: {updated_published_true}")
        print(f"   • Documents with published = False: {updated_published_false}")
        
        # Show sample updated documents
        print("\n📄 Sample documents after update:")
        sample_docs = list(collection.find(
            {},
            {'_id': 1, 'id': 1, 'title': 1, 'published': 1}
        ).limit(5))
        
        for i, doc in enumerate(sample_docs, 1):
            print(f"\n   Document {i}:")
            print(f"      _id: {doc.get('_id')}")
            print(f"      id: {doc.get('id', 'N/A')}")
            print(f"      title: {doc.get('title', 'N/A')}")
            print(f"      published: {doc.get('published', 'MISSING')}")
        
        # Close the connection
        client.close()
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 FINAL SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully added 'published: true' to {result.modified_count} document(s)")
        print(f"✅ All {total_count} documents now have the 'published' field")
        print("=" * 60)
        
        return True
        
    except ConnectionFailure as e:
        print(f"❌ ERROR: Failed to connect to MongoDB")
        print(f"   Details: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: Unexpected error occurred")
        print(f"   Details: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Add 'published' Field to Journeys Collection")
    print("=" * 60)
    print()
    
    # Confirm action
    print("⚠️  This script will add 'published: true' to all documents")
    print("   in the 'journeys' collection that don't have this field.")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        success = add_published_field()
        print()
        exit(0 if success else 1)
    else:
        print("\n❌ Operation cancelled by user.")
        exit(0)

