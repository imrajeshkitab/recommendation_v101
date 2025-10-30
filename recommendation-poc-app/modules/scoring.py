"""
Scoring Module - Jaccard Similarity Algorithm
This module is designed to be modular and easily replaceable with other scoring algorithms.
"""

from typing import Set, Dict, List


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.
    
    Jaccard Similarity = |A ∩ B| / |A ∪ B|
    
    Args:
        set1: First set of tags
        set2: Second set of tags
    
    Returns:
        Jaccard similarity score (0.0 to 1.0)
    """
    if not set1 and not set2:
        return 0.0
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def calculate_score(user_tags: Dict[str, List[str]], content_tags: Dict[str, List[str]]) -> float:
    """
    Calculate overall similarity score between user tags and content tags.
    
    Process:
    1. For each tag category, calculate Jaccard similarity
    2. Return average similarity across all categories
    
    Args:
        user_tags: Dictionary of {category: [tags]} from user responses
        content_tags: Dictionary of {category: [tags]} from content
    
    Returns:
        Average Jaccard similarity score (0.0 to 1.0)
    """
    scores = []
    
    # Get all unique categories from both user and content tags
    all_categories = set(user_tags.keys()).union(set(content_tags.keys()))
    
    for category in all_categories:
        user_cat_tags = set(user_tags.get(category, []))
        content_cat_tags = set(content_tags.get(category, []))
        
        # Only calculate if at least one set has tags
        if user_cat_tags or content_cat_tags:
            similarity = jaccard_similarity(user_cat_tags, content_cat_tags)
            scores.append(similarity)
    
    # Return average score across all categories
    if not scores:
        return 0.0
    
    return sum(scores) / len(scores)


def calculate_all_content_scores(user_tags: Dict[str, List[str]], 
                                 all_content: Dict[str, Dict]) -> Dict[str, float]:
    """
    Calculate scores for all content items against user tags.
    
    Args:
        user_tags: Dictionary of {category: [tags]} from user responses
        all_content: Dictionary of {content_id: {title, cover_page, tags}}
    
    Returns:
        Dictionary of {content_id: score}
    """
    content_scores = {}
    
    for content_id, content_data in all_content.items():
        content_tags = content_data.get('tags', {})
        score = calculate_score(user_tags, content_tags)
        content_scores[content_id] = score
    
    return content_scores

