import os
import pandas as pd
from pymongo import MongoClient
from bson.binary import Binary, UuidRepresentation
from uuid import UUID
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Test script to verify we can map CSV ids to MongoDB UUID fields
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
        return
    
    # Check if 'id' and 'tags' columns exist
    if 'id' not in df.columns:
        print("❌ Error: 'id' column not found in CSV")
        return
    
    if 'tags' not in df.columns:
        print("❌ Error: 'tags' column not found in CSV")
        return
    
    # Test with first 3 rows that have tags
    test_rows = df[df['tags'].notna()].head(3)
    
    print(f"\n🧪 Testing mapping with {len(test_rows)} sample rows...\n")
    
    success_count = 0
    fail_count = 0
    
    for idx, row in test_rows.iterrows():
        csv_id = row['id']
        linear_id = row.get('linear_identifier', 'N/A')
        
        print(f"Testing: {linear_id}")
        print(f"  CSV id (string): {csv_id}")
        
        try:
            # Convert string to UUID
            uuid_obj = UUID(csv_id)
            print(f"  UUID object: {uuid_obj}")
            
            # Query MongoDB with UUID
            # Try different approaches
            
            # Approach 1: Direct UUID query
            doc = collection.find_one({'id': uuid_obj})
            
            if doc:
                print(f"  ✅ Found in MongoDB!")
                print(f"  MongoDB id type: {type(doc['id'])}")
                print(f"  MongoDB id value: {doc['id']}")
                success_count += 1
            else:
                # Approach 2: Try as Binary with UUID subtype
                binary_uuid = Binary.from_uuid(uuid_obj)
                doc = collection.find_one({'id': binary_uuid})
                
                if doc:
                    print(f"  ✅ Found in MongoDB (using Binary)!")
                    print(f"  MongoDB id type: {type(doc['id'])}")
                    success_count += 1
                else:
                    print(f"  ❌ Not found in MongoDB")
                    fail_count += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            fail_count += 1
        
        print()
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Total tested: {len(test_rows)}")
    print(f"✅ Successfully mapped: {success_count}")
    print(f"❌ Failed to map: {fail_count}")
    print("="*60)
    
    if success_count > 0:
        print("\n✨ Mapping is working! Safe to proceed with full update.")
    else:
        print("\n⚠️  Mapping failed. Need to investigate MongoDB id format.")
    
    client.close()

if __name__ == "__main__":
    main()

