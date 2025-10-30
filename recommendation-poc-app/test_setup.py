"""
Test Setup Script
Verifies that all components are working before running the main app.
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("🧪 Testing Recommendation App Setup")
print("=" * 60)

# Test 1: Environment variables
print("\n1️⃣ Checking environment variables...")
load_dotenv()
mongodb_url = os.getenv('MONGODB_URL')
if mongodb_url:
    print("   ✅ MONGODB_URL found")
else:
    print("   ❌ MONGODB_URL not found in .env file")
    print("   💡 Create a .env file with: MONGODB_URL=your-connection-string")
    sys.exit(1)

# Test 2: Import modules
print("\n2️⃣ Checking module imports...")
try:
    from pymongo import MongoClient
    print("   ✅ pymongo imported")
except ImportError:
    print("   ❌ pymongo not installed")
    print("   💡 Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import streamlit
    print("   ✅ streamlit imported")
except ImportError:
    print("   ❌ streamlit not installed")
    print("   💡 Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: MongoDB connection
print("\n3️⃣ Testing MongoDB connection...")
try:
    client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("   ✅ Connected to MongoDB")
except Exception as e:
    print(f"   ❌ Connection failed: {str(e)}")
    print("   💡 Check your MONGODB_URL and network connection")
    sys.exit(1)

# Test 4: Database and collections
print("\n4️⃣ Checking database and collections...")
db = client['kitab-prod-tables']
questions_collection = db['seed_onboarding_questions']
content_collection = db['bytes_tagged']

question_count = questions_collection.count_documents({})
content_count = content_collection.count_documents({'published': True})

print(f"   📋 Questions found: {question_count}")
print(f"   📚 Published content found: {content_count}")

if question_count == 0:
    print("   ⚠️  No questions found in seed_onboarding_questions")
    print("   💡 Verify the collection name and data")

if content_count == 0:
    print("   ⚠️  No published content found in bytes_tagged")
    print("   💡 Verify content has published: true and tags field")

# Test 5: Check question structure
print("\n5️⃣ Verifying question structure...")
sample_question = questions_collection.find_one({'sequence': 1})
if sample_question:
    has_sequence = 'sequence' in sample_question
    has_question = 'question' in sample_question
    has_type = 'type' in sample_question
    has_options = 'options' in sample_question
    has_option_tags = 'option_tags' in sample_question
    
    print(f"   {'✅' if has_sequence else '❌'} sequence field")
    print(f"   {'✅' if has_question else '❌'} question field")
    print(f"   {'✅' if has_type else '❌'} type field")
    print(f"   {'✅' if has_options else '❌'} options field")
    print(f"   {'✅' if has_option_tags else '❌'} option_tags field")
    
    if not has_option_tags:
        print("\n   💡 Run setup_question_tags.py to add option_tags to questions")
else:
    print("   ❌ No question with sequence 1 found")

# Test 6: Check content structure
print("\n6️⃣ Verifying content structure...")
sample_content = content_collection.find_one({'published': True})
if sample_content:
    has_title = 'title' in sample_content
    has_tags = 'tags' in sample_content
    has_cover = 'cover_page' in sample_content
    
    print(f"   {'✅' if has_title else '❌'} title field")
    print(f"   {'✅' if has_cover else '❌'} cover_page field")
    print(f"   {'✅' if has_tags else '❌'} tags field")
    
    if has_tags:
        tag_categories = sample_content['tags'].keys()
        print(f"   📑 Tag categories: {', '.join(tag_categories)}")
else:
    print("   ❌ No published content found")

# Test 7: Test scoring module
print("\n7️⃣ Testing scoring module...")
try:
    from modules.scoring import calculate_score, jaccard_similarity
    
    # Test Jaccard similarity
    set1 = {"tag1", "tag2", "tag3"}
    set2 = {"tag2", "tag3", "tag4"}
    similarity = jaccard_similarity(set1, set2)
    expected = 2/4  # intersection=2, union=4
    
    if abs(similarity - expected) < 0.001:
        print(f"   ✅ Jaccard similarity working (got {similarity:.2f})")
    else:
        print(f"   ❌ Jaccard similarity incorrect (got {similarity}, expected {expected})")
    
    # Test calculate_score
    user_tags = {
        "primary_need": ["peace", "balance"],
        "motivation_driver": ["inner peace"]
    }
    content_tags = {
        "primary_need": ["peace", "growth"],
        "motivation_driver": ["inner peace", "clarity"]
    }
    score = calculate_score(user_tags, content_tags)
    print(f"   ✅ calculate_score working (sample score: {score:.2f})")
    
except Exception as e:
    print(f"   ❌ Scoring module error: {str(e)}")

# Test 8: Test config
print("\n8️⃣ Testing configuration...")
try:
    from utils.config import (
        QUESTION_TAG_MAPPING,
        TAG_CATEGORIES,
        TOP_K_RECOMMENDATIONS
    )
    print(f"   ✅ Config loaded")
    print(f"   📊 Top K recommendations: {TOP_K_RECOMMENDATIONS}")
    print(f"   🗺️  Question mappings: {len(QUESTION_TAG_MAPPING)}")
    print(f"   🏷️  Tag categories: {len(TAG_CATEGORIES)}")
except Exception as e:
    print(f"   ❌ Config error: {str(e)}")

# Summary
print("\n" + "=" * 60)
if question_count > 0 and content_count > 0:
    print("🎉 Setup verification complete! Ready to run the app.")
    print("\n▶️  Run the app with: streamlit run app.py")
else:
    print("⚠️  Setup incomplete. Please address the issues above.")
print("=" * 60)

client.close()

