"""
Content Similarity Module - Jaccard Similarity for Content-to-Content Comparison
Adapted from scoring.py for comparing content tags against other content tags.
"""

from typing import Dict, List, Tuple
from modules.scoring import jaccard_similarity


def calculate_content_similarity(content_tags_a: Dict[str, List[str]], 
                                 content_tags_b: Dict[str, List[str]]) -> float:
    """
    Calculate similarity between two content items based on their tags.
    
    Uses Jaccard similarity across all tag categories and returns the average.
    
    Args:
        content_tags_a: Dictionary of {category: [tags]} from first content item
        content_tags_b: Dictionary of {category: [tags]} from second content item
    
    Returns:
        Average Jaccard similarity score (0.0 to 1.0)
    """
    scores = []
    
    # Get all unique categories from both content items
    all_categories = set(content_tags_a.keys()).union(set(content_tags_b.keys()))
    
    for category in all_categories:
        tags_a = set(content_tags_a.get(category, []))
        tags_b = set(content_tags_b.get(category, []))
        
        # Only calculate if at least one set has tags
        if tags_a or tags_b:
            similarity = jaccard_similarity(tags_a, tags_b)
            scores.append(similarity)
    
    # Return average score across all categories
    if not scores:
        return 0.0
    
    return sum(scores) / len(scores)


def find_similar_content(target_content_id: str, 
                        all_content: Dict[str, Dict], 
                        top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Find the most similar content items to a target content item.
    
    Args:
        target_content_id: The ID of the target content item
        all_content: Dictionary of all content items {content_id: {tags, title, ...}}
        top_k: Number of similar items to return (default: 5)
    
    Returns:
        List of tuples (content_id, similarity_score) sorted by score descending
    """
    if target_content_id not in all_content:
        return []
    
    target_tags = all_content[target_content_id].get('tags', {})
    
    # Calculate similarity scores for all other content
    similarity_scores = []
    
    for content_id, content_data in all_content.items():
        # Skip the target content itself
        if content_id == target_content_id:
            continue
        
        content_tags = content_data.get('tags', {})
        score = calculate_content_similarity(target_tags, content_tags)
        
        # Only include content with non-zero similarity
        if score > 0:
            similarity_scores.append((content_id, score))
    
    # Sort by similarity score (descending) and return top K
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    
    return similarity_scores[:top_k]

