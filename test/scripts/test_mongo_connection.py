"""
MongoDB Connection Test Script

This script tests the connection to MongoDB using MONGODB_URL2 from .env file
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

def test_mongodb_connection():
    """
    Test MongoDB connection using MONGODB_URL2 from environment variables
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get MongoDB URL from environment
    mongodb_url = os.getenv('MONGODB_URL2')
    
    if not mongodb_url:
        print("❌ ERROR: MONGODB_URL2 not found in .env file")
        return False
    
    print(f"🔍 Testing MongoDB connection...")
    print(f"   Connection string found (length: {len(mongodb_url)} characters)")
    
    try:
        # Create MongoDB client with a timeout
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        print("✅ SUCCESS: Connected to MongoDB successfully!")
        
        # Get server info
        server_info = client.server_info()
        print(f"   MongoDB version: {server_info.get('version', 'Unknown')}")
        
        # List available databases
        db_list = client.list_database_names()
        print(f"   Available databases: {', '.join(db_list)}")
        
        # Close the connection
        client.close()
        print("\n✅ Connection test completed successfully!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ ERROR: Failed to connect to MongoDB")
        print(f"   Details: {str(e)}")
        return False
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ ERROR: Server selection timeout")
        print(f"   Details: Could not connect to MongoDB server within timeout period")
        print(f"   Please check if the MongoDB server is running and accessible")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: Unexpected error occurred")
        print(f"   Details: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    print()
    
    success = test_mongodb_connection()
    
    print()
    print("=" * 60)
    
    # Exit with appropriate code
    exit(0 if success else 1)

