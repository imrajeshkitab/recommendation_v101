"""
Database Client Module - MongoDB Operations
Handles all database connections and queries.
"""

import json
from typing import List, Dict, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import streamlit as st

from utils.config import (
    MONGODB_URL, 
    DATABASE_NAME, 
    QUESTIONS_COLLECTION, 
    CONTENT_COLLECTION
)


class DatabaseClient:
    """MongoDB client for fetching questions and content."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        if not MONGODB_URL:
            raise ValueError("MONGODB_URL not found in environment variables")
        
        self.client = MongoClient(MONGODB_URL, uuidRepresentation='standard')
        self.db = self.client[DATABASE_NAME]
        
        # Test connection
        try:
            self.client.admin.command('ping')
        except ConnectionFailure:
            raise ConnectionFailure("Failed to connect to MongoDB")
    
    def get_questions(self) -> List[Dict]:
        """
        Fetch all onboarding questions sorted by sequence.
        
        Returns:
            List of question documents with option_tags
        """
        try:
            collection = self.db[QUESTIONS_COLLECTION]
            
            # Fetch questions sorted by sequence
            questions = list(collection.find({}).sort('sequence', 1))
            
            # Process questions to ensure proper format
            for question in questions:
                # Convert ObjectId to string for JSON serialization
                if '_id' in question:
                    question['_id'] = str(question['_id'])
                
                # Parse JSON strings if needed
                if isinstance(question.get('options'), str):
                    question['options'] = json.loads(question['options'])
                
                if isinstance(question.get('images'), str):
                    question['images'] = json.loads(question['images'])
                
                # Ensure option_tags exists (from MongoDB if available)
                if 'option_tags' not in question:
                    question['option_tags'] = {}
            
            return questions
        
        except Exception as e:
            st.error(f"Error fetching questions: {str(e)}")
            return []
    
    def get_all_content(self) -> Dict[str, Dict]:
        """
        Fetch all content from bytes_tagged collection.
        
        Returns:
            Dictionary of {content_id: {title, cover_page, author, category, tags}}
        """
        try:
            collection = self.db[CONTENT_COLLECTION]
            
            # Fetch all content with tags
            content_docs = list(collection.find(
                {'published': True, 'tags': {'$exists': True}},
                {
                    'id': 1,
                    'title': 1,
                    'cover_page': 1,
                    'author': 1,
                    'category': 1,
                    'tags': 1,
                    '_id': 1
                }
            ))
            
            # Convert to dictionary format
            all_content = {}
            for doc in content_docs:
                # Use string version of _id as key
                content_id = str(doc['_id'])
                
                all_content[content_id] = {
                    'title': doc.get('title', 'Untitled'),
                    'cover_page': doc.get('cover_page', ''),
                    'author': doc.get('author', ''),
                    'category': doc.get('category', ''),
                    'tags': doc.get('tags', {})
                }
            
            return all_content
        
        except Exception as e:
            st.error(f"Error fetching content: {str(e)}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


@st.cache_resource
def get_db_client() -> DatabaseClient:
    """
    Get cached database client (Streamlit will maintain single instance).
    
    Returns:
        DatabaseClient instance
    """
    return DatabaseClient()

