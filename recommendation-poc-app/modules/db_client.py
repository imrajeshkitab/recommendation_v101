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
    
    def get_all_content_for_discovery(self) -> Dict[str, Dict]:
        """
        Fetch all content from bytes, summaries, and journeys collections for discovery.
        
        Returns:
            Dictionary of {content_id: {title, cover_page, author, category, tags, content_type, content}}
        """
        try:
            all_content = {}
            
            # Collection configurations: (collection_name, content_type_label)
            collections = [
                ('bytes', 'byte'),
                ('summaries', 'summary'),
                ('journeys', 'journey')
            ]
            
            for collection_name, content_type in collections:
                collection = self.db[collection_name]
                
                # Fetch all published content with tags
                content_docs = list(collection.find(
                    {'published': True, 'tags': {'$exists': True}},
                    {
                        'id': 1,
                        'title': 1,
                        'cover_page': 1,
                        'author': 1,
                        'category': 1,
                        'tags': 1,
                        'content': 1,
                        '_id': 1
                    }
                ))
                
                # Convert to dictionary format
                for doc in content_docs:
                    # Use string version of _id as key with type prefix
                    content_id = f"{content_type}_{str(doc['_id'])}"
                    
                    all_content[content_id] = {
                        'title': doc.get('title', 'Untitled'),
                        'cover_page': doc.get('cover_page', ''),
                        'author': doc.get('author', ''),
                        'category': doc.get('category', ''),
                        'tags': doc.get('tags', {}),
                        'content_type': content_type,
                        'content': doc.get('content', ''),
                        'original_id': str(doc['_id'])
                    }
            
            return all_content
        
        except Exception as e:
            st.error(f"Error fetching content for discovery: {str(e)}")
            return {}
    
    def search_content_by_title(self, query: str, filters: List[str]) -> Dict[str, Dict]:
        """
        Search content by title across selected collections.
        
        Args:
            query: Search query string
            filters: List of content types to search in ['bytes', 'summaries', 'journeys']
        
        Returns:
            Dictionary of {content_id: {title, cover_page, author, category, tags, content_type}}
        """
        try:
            results = {}
            
            # Map filter names to collection names
            filter_mapping = {
                'bytes': ('bytes', 'byte'),
                'summaries': ('summaries', 'summary'),
                'journeys': ('journeys', 'journey')
            }
            
            # Search in selected collections only
            for filter_name in filters:
                if filter_name not in filter_mapping:
                    continue
                
                collection_name, content_type = filter_mapping[filter_name]
                collection = self.db[collection_name]
                
                # Case-insensitive search on title
                search_query = {
                    'published': True,
                    'tags': {'$exists': True},
                    'title': {'$regex': query, '$options': 'i'}
                }
                
                # Limit to 10 results per collection (total max 30)
                content_docs = list(collection.find(
                    search_query,
                    {
                        'id': 1,
                        'title': 1,
                        'cover_page': 1,
                        'author': 1,
                        'category': 1,
                        'tags': 1,
                        'content': 1,
                        '_id': 1
                    }
                ).limit(10))
                
                # Convert to dictionary format
                for doc in content_docs:
                    content_id = f"{content_type}_{str(doc['_id'])}"
                    
                    results[content_id] = {
                        'title': doc.get('title', 'Untitled'),
                        'cover_page': doc.get('cover_page', ''),
                        'author': doc.get('author', ''),
                        'category': doc.get('category', ''),
                        'tags': doc.get('tags', {}),
                        'content_type': content_type,
                        'content': doc.get('content', ''),
                        'original_id': str(doc['_id'])
                    }
            
            return results
        
        except Exception as e:
            st.error(f"Error searching content: {str(e)}")
            return {}
    
    def get_content_by_id(self, content_id: str, content_type: str) -> Optional[Dict]:
        """
        Retrieve a specific content item by ID and type.
        
        Args:
            content_id: The MongoDB _id of the content
            content_type: Type of content ('byte', 'summary', 'journey')
        
        Returns:
            Dictionary with content details or None
        """
        try:
            from bson import ObjectId
            
            # Map content type to collection name
            type_to_collection = {
                'byte': 'bytes',
                'summary': 'summaries',
                'journey': 'journeys'
            }
            
            collection_name = type_to_collection.get(content_type)
            if not collection_name:
                return None
            
            collection = self.db[collection_name]
            
            # Fetch the specific content
            doc = collection.find_one(
                {'_id': ObjectId(content_id)},
                {
                    'id': 1,
                    'title': 1,
                    'cover_page': 1,
                    'author': 1,
                    'category': 1,
                    'tags': 1,
                    'content': 1,
                    '_id': 1
                }
            )
            
            if not doc:
                return None
            
            return {
                'title': doc.get('title', 'Untitled'),
                'cover_page': doc.get('cover_page', ''),
                'author': doc.get('author', ''),
                'category': doc.get('category', ''),
                'tags': doc.get('tags', {}),
                'content_type': content_type,
                'content': doc.get('content', ''),
                'original_id': str(doc['_id'])
            }
        
        except Exception as e:
            st.error(f"Error fetching content by ID: {str(e)}")
            return None
    
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

