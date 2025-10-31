"""
Query Search Module
Handles natural language query-based content search using tag extraction and ranking
"""

import json
import logging
from typing import List, Dict, Set, Tuple, Optional

from modules.gemini_service import generate_json_response
from modules.scoring import jaccard_similarity

logger = logging.getLogger(__name__)


# JSON schema for tag extraction
TAG_EXTRACTION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "tags": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        }
    },
    "required": ["tags"]
}


# Prompt template for tag extraction
PROMPT_TEMPLATE = """You are a content recommendation system that extracts relevant tags from user queries.

Based on possible tags across these 8 categories:

1. **Life Stage - Age**: young adult, early twenties, Gen Z, millennials, young professional, career building, mid-career, Gen X, established professional, midlife, mature, senior, wisdom seeker, retirement planning, legacy building

2. **Life Stage - Relationship**: independent, solo, dating, single, partnered, committed, couple, romantic bond, married, spouse, family unit, divorced, separated, widowed, loss, grief, new beginning

3. **Life Stage - Parenting**: parent, caregiver, family, children, parenting journey, childless, child-free, independent, personal freedom

4. **Primary Need**: peace, balance, stress relief, mental health, tranquility, mindfulness, emotional stability, self-esteem, confidence building, self-assurance, empowerment, self-belief, courage, connection, communication, intimacy, relationship skills, empathy, social bonds, direction, purpose, career guidance, life path, decision making, clarity seeking, personal growth, self-improvement, development, potential, transformation, curiosity, knowledge seeker, lifelong learning, intellectual growth, exploration, discovery

5. **Motivation Driver**: inner peace, serenity, calm, meditation, harmony, productivity, efficiency, work-life balance, goal achievement, stress management, success, self-discovery, identity, authenticity, introspection, self-awareness, relationships, caregiving, empathy, love, support, interpersonal skills, meaning, life purpose, vision, mission, clarity, path finding, decision making, wisdom, judgment, priorities, values, intentional living

6. **Cognitive Style**: analytical, rational, logical thinker, planner, strategic, systematic, empathetic, values-driven, emotional, ethical, compassionate, practical, detail-oriented, realistic, concrete, present-focused, intuitive, visionary, creative, innovative, imaginative, future-focused

7. **Content Depth**: busy, time-constrained, quick learner, efficient, brief sessions, micro-learning, moderate commitment, balanced, daily habit, consistent, story lover, regular practice, dedicated, deep learner, committed, intensive, thorough, wisdom seeker, patient

8. **Learning Style**: methodical, patient, gradual progress, systematic learner, steady growth, incremental, energetic, impact-driven, dynamic, transformational, bold, high-intensity, reflective, philosophical, contemplative, analytical, introspective, thoughtful, practical, results-oriented, pragmatic, action-focused, no-nonsense

---

Extract relevant tags from this user query:
"{query}"

Analyze the user's needs, challenges, goals, and situation expressed in the query.
Return a flat list of relevant tags that would help match content addressing their needs.
Use tags from the categories listed above, but you can also infer similar relevant tags.

Examples:
- Query: "I am losing my authority, I want to improve my leadership"
  Tags: ["leadership", "authority", "confidence", "self-assurance", "empowerment", "career", "management", "influence", "growth", "development"]

- Query: "I feel stressed and need peace"
  Tags: ["stress relief", "peace", "calm", "mental health", "balance", "tranquility", "mindfulness", "inner peace", "serenity"]

Return ONLY a JSON object in this format:
{{"tags": ["tag1", "tag2", "tag3", ...]}}
"""


def extract_tags_from_query(query: str) -> Optional[List[str]]:
    """
    Extract relevant tags from a user's natural language query using Gemini API.
    
    Args:
        query: The user's search query
        
    Returns:
        List of extracted tags, or None if extraction failed
    """
    if not query or not query.strip():
        logger.warning("Empty query provided for tag extraction")
        return None
    
    try:
        # Build the prompt
        prompt = PROMPT_TEMPLATE.format(query=query.strip())
        
        # Call Gemini API
        response_json = generate_json_response(
            prompt=prompt,
            json_schema=TAG_EXTRACTION_SCHEMA
        )
        
        if not response_json:
            logger.error("Failed to get response from Gemini API")
            return None
        
        # Parse the JSON response
        response_data = json.loads(response_json)
        tags = response_data.get("tags", [])
        
        logger.info(f"Extracted {len(tags)} tags from query: {tags}")
        return tags
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting tags from query: {e}")
        return None


def flatten_content_tags(content_tags: Dict[str, List[str]]) -> Set[str]:
    """
    Flatten content's categorized tag structure into a single set of tags.
    
    Args:
        content_tags: Dictionary with tag categories as keys and tag lists as values
                     Example: {"primary_need": ["growth"], "motivation_driver": ["clarity"]}
    
    Returns:
        Set of all tags from all categories
        Example: {"growth", "clarity"}
    """
    flattened = set()
    
    if not content_tags or not isinstance(content_tags, dict):
        return flattened
    
    for category, tags in content_tags.items():
        if isinstance(tags, list):
            # Convert all tags to lowercase for case-insensitive matching
            flattened.update(tag.lower() for tag in tags if isinstance(tag, str))
    
    return flattened


def rank_content_by_tags(
    query_tags: List[str], 
    all_content: Dict[str, Dict], 
    filters: List[str]
) -> List[Tuple[str, float]]:
    """
    Rank content items by similarity to query tags using Jaccard similarity.
    
    Args:
        query_tags: List of tags extracted from user query
        all_content: Dictionary of {content_id: {title, cover_page, tags, content_type, ...}}
        filters: List of content types to include ['bytes', 'summaries', 'journeys']
    
    Returns:
        List of (content_id, score) tuples, sorted by score descending, top 10 items
    """
    if not query_tags:
        logger.warning("No query tags provided for ranking")
        return []
    
    # Convert query tags to lowercase set
    query_tag_set = set(tag.lower() for tag in query_tags)
    
    # Map filter names to content types
    filter_mapping = {
        'bytes': 'byte',
        'summaries': 'summary',
        'journeys': 'journey'
    }
    content_types = [filter_mapping.get(f, f) for f in filters]
    
    # Calculate scores for each content item
    content_scores = []
    
    for content_id, content_data in all_content.items():
        # Apply filter
        if content_data.get('content_type') not in content_types:
            continue
        
        # Flatten content tags
        content_tags = content_data.get('tags', {})
        content_tag_set = flatten_content_tags(content_tags)
        
        # Skip if content has no tags
        if not content_tag_set:
            continue
        
        # Calculate Jaccard similarity
        score = jaccard_similarity(query_tag_set, content_tag_set)
        
        # Only include if there's some match
        if score > 0:
            content_scores.append((content_id, score))
    
    # Sort by score descending and return top 10
    content_scores.sort(key=lambda x: x[1], reverse=True)
    top_results = content_scores[:10]
    
    logger.info(f"Ranked {len(content_scores)} content items, returning top {len(top_results)}")
    
    return top_results

