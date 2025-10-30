"""
Setup Script: Load option_tags into MongoDB questions collection
This script reads the questionnaire-tags.csv and adds option_tags to each question in MongoDB.
"""

import os
import sys
import json
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()


def parse_tags(tags_str):
    """Parse tags from string representation of list."""
    if not tags_str or pd.isna(tags_str):
        return []
    
    try:
        # Remove quotes and brackets, split by comma
        tags_str = tags_str.strip('[]"\'')
        tags = [tag.strip().strip('"\'') for tag in tags_str.split(',')]
        return [tag for tag in tags if tag]
    except:
        try:
            # Try JSON parsing
            return json.loads(tags_str)
        except:
            return []


def main():
    """Load option tags from CSV and update MongoDB questions."""
    
    # Get MongoDB connection
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("❌ Error: MONGODB_URL not found in .env file")
        return
    
    print("🔌 Connecting to MongoDB...")
    try:
        client = MongoClient(mongodb_url, uuidRepresentation='standard')
        db = client['kitab-prod-tables']
        collection = db['seed_onboarding_questions']
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return
    
    # Read CSV file
    csv_path = '../database/tables/questionnaire-tags.csv'
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"📖 Reading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Group by question
    questions_data = {}
    for _, row in df.iterrows():
        q_num = row['Question Number']
        option_num = str(row['Option Number'])
        tags = parse_tags(row['Relevant Tags'])
        
        if q_num not in questions_data:
            questions_data[q_num] = {}
        
        questions_data[q_num][option_num] = tags
    
    print(f"\n📝 Parsed tags for {len(questions_data)} questions")
    
    # Update MongoDB documents
    updated_count = 0
    for q_num, option_tags in questions_data.items():
        # Extract sequence number from Q1, Q2, etc.
        sequence = int(q_num.replace('Q', ''))
        
        # Update the document
        result = collection.update_one(
            {'sequence': sequence},
            {'$set': {'option_tags': option_tags}}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            print(f"✅ Updated {q_num} (sequence: {sequence}) with {len(option_tags)} options")
    
    print(f"\n🎉 Successfully updated {updated_count} questions in MongoDB!")
    
    # Show sample
    print("\n📋 Sample question with option_tags:")
    sample = collection.find_one({'sequence': 1})
    if sample:
        print(f"Question: {sample.get('question')}")
        print(f"Option tags: {json.dumps(sample.get('option_tags', {}), indent=2)}")
    
    client.close()


if __name__ == "__main__":
    main()

