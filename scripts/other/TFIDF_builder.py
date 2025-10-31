import math
from typing import Set, Dict, List
from collections import defaultdict

# (Your existing jaccard_similarity function can stay if you want)

def build_idf_model(all_content: Dict[str, Dict], 
                    total_docs: int) -> Dict[str, Dict[str, float]]:
    """
    Calculates the IDF score for every tag within its category.
    
    Args:
        all_content: Your dictionary of 50k content items.
        total_docs: The total number of content items (e.g., 50000).
    
    Returns:
        A dictionary structured as {category: {tag: idf_score}}
    """
    # 1. Count Document Frequencies (DF) for each tag *per category*
    # {category: {tag: count}}
    category_df = defaultdict(lambda: defaultdict(int))
    
    for content_id, content_data in all_content.items():
        content_tags = content_data.get('tags', {})
        for category, tags in content_tags.items():
            # Use set() to ensure a tag is only counted once per document
            for tag in set(tags):
                category_df[category][tag] += 1
                
    # 2. Calculate IDF scores from DF counts
    # {category: {tag: idf}}
    idf_model = defaultdict(dict)
    
    for category, tag_counts in category_df.items():
        for tag, count in tag_counts.items():
            # IDF = log(Total Docs / Docs with Tag)
            # We use (1 + count) for "smoothing" to avoid division by zero
            # if a tag is new and has a count of 0 (though it shouldn't here).
            idf_score = math.log(total_docs / (1 + count))
            idf_model[category][tag] = idf_score
            
    return idf_model