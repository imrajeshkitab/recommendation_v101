"""
Check if the 'journeys' collection in MongoDB has a 'published' field

This script connects to the MongoDB database and analyzes the 'journeys' collection
to determine if documents have a 'published' field.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from collections import Counter

def check_published_field():
    """
    Check if journeys collection has a 'published' field
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
        
        # Get total count
        total_count = collection.count_documents({})
        print(f"\n📊 Total documents in 'journeys' collection: {total_count}")
        
        if total_count == 0:
            print("⚠️  Collection is empty!")
            client.close()
            return True
        
        # Check for 'published' field
        print("\n🔎 Checking for 'published' field...")
        
        # Count documents with 'published' field
        with_published = collection.count_documents({'published': {'$exists': True}})
        without_published = total_count - with_published
        
        print(f"   ✓ Documents WITH 'published' field: {with_published}")
        print(f"   ✗ Documents WITHOUT 'published' field: {without_published}")
        
        if with_published > 0:
            # Check the values of 'published' field
            print("\n📈 Analyzing 'published' field values...")
            
            published_true = collection.count_documents({'published': True})
            published_false = collection.count_documents({'published': False})
            
            print(f"   • published = True: {published_true}")
            print(f"   • published = False: {published_false}")
            
            # Sample documents with published field
            print("\n📄 Sample documents with 'published' field:")
            sample_docs = list(collection.find(
                {'published': {'$exists': True}},
                {'_id': 1, 'id': 1, 'title': 1, 'published': 1}
            ).limit(5))
            
            for i, doc in enumerate(sample_docs, 1):
                print(f"\n   Sample {i}:")
                print(f"      _id: {doc.get('_id')}")
                print(f"      id: {doc.get('id', 'N/A')}")
                print(f"      title: {doc.get('title', 'N/A')}")
                print(f"      published: {doc.get('published')}")
        
        if without_published > 0:
            # Sample documents without published field
            print("\n📄 Sample documents WITHOUT 'published' field:")
            sample_docs_no_published = list(collection.find(
                {'published': {'$exists': False}},
                {'_id': 1, 'id': 1, 'title': 1}
            ).limit(3))
            
            for i, doc in enumerate(sample_docs_no_published, 1):
                print(f"\n   Sample {i}:")
                print(f"      _id: {doc.get('_id')}")
                print(f"      id: {doc.get('id', 'N/A')}")
                print(f"      title: {doc.get('title', 'N/A')}")
        
        # Get all field names from a sample document
        print("\n🗂️  All fields in a sample document:")
        sample = collection.find_one()
        if sample:
            fields = list(sample.keys())
            print(f"   Fields: {', '.join(fields)}")
        
        # Close the connection
        client.close()
        print("\n✅ Check completed successfully!")
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        if with_published == total_count:
            print("✅ ALL documents have the 'published' field")
        elif with_published > 0:
            print(f"⚠️  PARTIAL: {with_published}/{total_count} documents have 'published' field")
        else:
            print("❌ NO documents have the 'published' field")
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
    print("MongoDB 'journeys' Collection - 'published' Field Check")
    print("=" * 60)
    print()
    
    success = check_published_field()
    
    print()
    
    # Exit with appropriate code
    exit(0 if success else 1)

