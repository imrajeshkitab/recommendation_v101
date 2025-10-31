"""
Content Discovery Page
Explore content through search and similarity-based recommendations
"""

import streamlit as st
import random
from typing import Dict, List, Optional

from modules.db_client import get_db_client
from modules.content_similarity import find_similar_content
from modules.query_search import extract_tags_from_query, rank_content_by_tags


# Page Configuration
st.set_page_config(
    page_title="Discover Content",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Custom CSS for modern styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .main {
        padding: 1rem;
    }
    
    /* Reduce default Streamlit spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Reduce gap between elements */
    div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
        gap: 0.5rem;
    }
    
    /* Search container */
    .search-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 20px;
        margin-bottom: 0.8rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .search-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        text-align: center;
    }
    
    /* Content card */
    .content-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .content-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* Content viewer */
    .content-viewer {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .content-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.25rem;
        line-height: 1.3;
    }
    
    .content-author {
        font-size: 0.85rem;
        color: #7f8c8d;
        margin-bottom: 0.5rem;
    }
    
    .content-category {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }
    
    .content-type-badge {
        display: inline-block;
        background: #e8f4f8;
        color: #2980b9;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        margin-left: 0.4rem;
    }
    
    /* Similar content section */
    .similar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
    }
    
    /* Search result item */
    .search-result {
        padding: 0.4rem;
        margin-bottom: 0.4rem;
    }
    
    /* Filter chips */
    .filter-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Similarity score badge */
    .similarity-score {
        display: inline-block;
        background: #2ecc71;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    /* Ensure consistent input height */
    input[type="text"] {
        height: 2.5rem !important;
    }
    
    /* Adjust button height to match input */
    div[data-testid="stButton"] > button {
        height: 2.5rem;
        padding: 0.5rem 1rem;
    }
    
    /* Style the clear button to be smaller and round */
    button[key="clear_inline"] {
        width: 2.5rem !important;
        height: 2.5rem !important;
        padding: 0 !important;
        border-radius: 50% !important;
        font-size: 1.2rem !important;
        line-height: 1 !important;
    }
</style>
""", unsafe_allow_html=True)


def optimize_image_url(url: str, width: int = 380, resize: str = "contain") -> str:
    """
    Optimize Supabase image URL using the render/image endpoint with transformation parameters.
    """
    if not url:
        return url
    
    # Only optimize Supabase URLs
    if 'supabase.co' in url:
        # Replace /object with /render/image for image transformation API
        optimized_url = url.replace('/storage/v1/object/', '/storage/v1/render/image/')
        
        # Add transformation parameters
        separator = '&' if '?' in optimized_url else '?'
        return f"{optimized_url}{separator}width={width}&resize={resize}"
    
    return url


def initialize_discovery_state():
    """Initialize session state variables for discovery page."""
    if 'all_discovery_content' not in st.session_state:
        db_client = get_db_client()
        st.session_state.all_discovery_content = db_client.get_all_content_for_discovery()
    
    if 'selected_content_id' not in st.session_state:
        # Select random content on initial load
        if st.session_state.all_discovery_content:
            random_id = random.choice(list(st.session_state.all_discovery_content.keys()))
            st.session_state.selected_content_id = random_id
        else:
            st.session_state.selected_content_id = None
    
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = {}
    
    if 'active_filters' not in st.session_state:
        st.session_state.active_filters = ['bytes', 'summaries', 'journeys']
    
    # Query search session state
    if 'query_search_input' not in st.session_state:
        st.session_state.query_search_input = ""
    
    if 'query_search_results' not in st.session_state:
        st.session_state.query_search_results = []
    
    if 'query_extracted_tags' not in st.session_state:
        st.session_state.query_extracted_tags = []
    
    # Search mode toggle
    if 'search_mode' not in st.session_state:
        st.session_state.search_mode = 'title'  # 'title' or 'query'


def handle_content_click(content_id: str):
    """Handle click on a content item to display it."""
    st.session_state.selected_content_id = content_id
    st.session_state.search_query = ""
    st.session_state.search_results = {}
    st.session_state.query_search_input = ""
    st.session_state.query_search_results = []
    st.session_state.query_extracted_tags = []


def get_random_content_from_filters(filters: List[str]) -> Optional[str]:
    """
    Get a random content ID from the selected filter types.
    
    Args:
        filters: List of content types ['bytes', 'summaries', 'journeys']
    
    Returns:
        Random content ID or None if no matching content
    """
    if not filters or not st.session_state.all_discovery_content:
        return None
    
    # Map filter names to content types (plural to singular)
    filter_mapping = {
        'bytes': 'byte',
        'summaries': 'summary',
        'journeys': 'journey'
    }
    
    # Convert filter names to content types
    content_types = [filter_mapping.get(f, f) for f in filters]
    
    # Filter content by type
    filtered_content = [
        content_id for content_id, content in st.session_state.all_discovery_content.items()
        if content.get('content_type') in content_types
    ]
    
    if filtered_content:
        return random.choice(filtered_content)
    
    return None


def display_unified_search_bar():
    """Display unified search bar with mode toggle and filter options."""
    st.markdown("""
    <div class="search-container">
        <div class="search-title">🔍 Discover Content</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Search mode toggle
    col_mode1, col_mode2 = st.columns([1, 1])
    with col_mode1:
        if st.button(
            "📝 Title Search" if st.session_state.search_mode == 'query' else "✅ Title Search",
            use_container_width=True,
            type="primary" if st.session_state.search_mode == 'title' else "secondary",
            key="toggle_title"
        ):
            st.session_state.search_mode = 'title'
            st.session_state.query_search_input = ""
            st.session_state.query_search_results = []
            st.session_state.query_extracted_tags = []
            st.rerun()
    
    with col_mode2:
        if st.button(
            "🤖 Smart Query" if st.session_state.search_mode == 'title' else "✅ Smart Query",
            use_container_width=True,
            type="primary" if st.session_state.search_mode == 'query' else "secondary",
            key="toggle_query"
        ):
            st.session_state.search_mode = 'query'
            st.session_state.search_query = ""
            st.session_state.search_results = {}
            st.rerun()
    
    # Search input based on mode
    col1, col_clear, col2 = st.columns([3, 0.3, 1])
    
    with col1:
        if st.session_state.search_mode == 'title':
            search_input = st.text_input(
                "Search by title",
                placeholder="Enter search term...",
                label_visibility="collapsed",
                key="search_input"
            )
        else:
            # Use container to control height
            search_input = st.text_input(
                "Your query",
                placeholder="e.g., I want to be a better parent",
                label_visibility="collapsed",
                key="query_input_widget"
            )
    
    with col_clear:
        # Show clear button only when there's an active search
        if (st.session_state.search_mode == 'title' and st.session_state.search_query) or \
           (st.session_state.search_mode == 'query' and st.session_state.query_search_input):
            if st.button("✕", key="clear_inline", use_container_width=True, help="Clear search"):
                if st.session_state.search_mode == 'title':
                    st.session_state.search_query = ""
                    st.session_state.search_results = {}
                else:
                    st.session_state.query_search_input = ""
                    st.session_state.query_search_results = []
                    st.session_state.query_extracted_tags = []
                st.rerun()
    
    with col2:
        if st.button("🔍 Search", use_container_width=True, type="primary", key="search_btn"):
            if search_input.strip():
                if st.session_state.search_mode == 'title':
                    st.session_state.search_query = search_input
                    perform_search()
                else:
                    perform_query_search(search_input)
                st.rerun()
            else:
                # Show random content from selected filters
                if st.session_state.search_mode == 'title' and st.session_state.active_filters:
                    random_content_id = get_random_content_from_filters(st.session_state.active_filters)
                    if random_content_id:
                        st.session_state.selected_content_id = random_content_id
                        st.session_state.search_query = ""
                        st.session_state.search_results = {}
                        st.rerun()
                    else:
                        st.warning("No content found in selected filters")
                else:
                    st.warning("Please enter a search term")
    
    # Filter checkboxes - directly below search without label
    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
    
    # Track filter changes
    new_filters = []
    
    with col_f1:
        if st.checkbox("Bytes", value='bytes' in st.session_state.active_filters, key="filter_bytes"):
            new_filters.append('bytes')
    
    with col_f2:
        if st.checkbox("Summaries", value='summaries' in st.session_state.active_filters, key="filter_summaries"):
            new_filters.append('summaries')
    
    with col_f3:
        if st.checkbox("Journeys", value='journeys' in st.session_state.active_filters, key="filter_journeys"):
            new_filters.append('journeys')
    
    # Update filters if changed
    if set(new_filters) != set(st.session_state.active_filters):
        st.session_state.active_filters = new_filters


def perform_search():
    """Execute search and store results."""
    if not st.session_state.search_query or not st.session_state.active_filters:
        st.session_state.search_results = {}
        return
    
    db_client = get_db_client()
    results = db_client.search_content_by_title(
        st.session_state.search_query,
        st.session_state.active_filters
    )
    
    # Limit to 10 results
    limited_results = dict(list(results.items())[:10])
    st.session_state.search_results = limited_results


def display_search_results():
    """Display search results if any."""
    # Show search status
    if st.session_state.search_query:
        if st.session_state.search_results:
            st.markdown(f"### Results ({len(st.session_state.search_results)})")
        else:
            st.info(f"No results found for '{st.session_state.search_query}'.")
    
    if not st.session_state.search_results:
        return
    
    # Display results in a scrollable area
    for i, (content_id, content) in enumerate(st.session_state.search_results.items()):
        if i > 0:  # Only add separator between items, not before first
            st.markdown("---")
            
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if content.get('cover_page'):
                st.image(optimize_image_url(content['cover_page'], width=380), use_container_width=True)
            else:
                st.markdown("📄")
        
        with col2:
            st.markdown(f"**{content['title']}**")
            st.caption(f"{content.get('author', 'Unknown')}")
            type_badge = content.get('content_type', 'unknown').capitalize()
            st.markdown(f"<span class='content-type-badge'>{type_badge}</span>", unsafe_allow_html=True)
            
            if st.button(f"View", key=f"view_{content_id}", type="secondary"):
                handle_content_click(content_id)
                st.rerun()


def perform_query_search(query: str):
    """Execute query-based search using tag extraction and ranking."""
    if not query or not query.strip():
        st.warning("Please enter a query to search.")
        return
    
    if not st.session_state.active_filters:
        st.warning("Please select at least one filter.")
        return
    
    try:
        with st.spinner("🤖 Analyzing your query and finding relevant content..."):
            # Extract tags from query
            extracted_tags = extract_tags_from_query(query)
            
            if not extracted_tags:
                st.error("Failed to extract tags from your query. Please try again or rephrase your query.")
                return
            
            # Store extracted tags
            st.session_state.query_extracted_tags = extracted_tags
            
            # Rank content by tags
            ranked_results = rank_content_by_tags(
                query_tags=extracted_tags,
                all_content=st.session_state.all_discovery_content,
                filters=st.session_state.active_filters
            )
            
            # Store results
            st.session_state.query_search_results = ranked_results
            st.session_state.query_search_input = query
            
    except Exception as e:
        st.error(f"An error occurred during search: {str(e)}")
        st.session_state.query_search_results = []
        st.session_state.query_extracted_tags = []


def display_query_search_results():
    """Display query search results with ranked content."""
    # Show search status
    if st.session_state.query_search_input:
        if st.session_state.query_search_results:
            st.markdown(f"### Results ({len(st.session_state.query_search_results)})")
        else:
            st.info(f"No matching content found. Try different keywords or filters.")
    
    if not st.session_state.query_search_results:
        return
    
    # Display ranked results directly without tags
    for i, (content_id, score) in enumerate(st.session_state.query_search_results):
        if content_id not in st.session_state.all_discovery_content:
            continue
        
        if i > 0:  # Only add separator between items
            st.markdown("---")
        
        content = st.session_state.all_discovery_content[content_id]
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if content.get('cover_page'):
                st.image(optimize_image_url(content['cover_page'], width=380), use_container_width=True)
            else:
                st.markdown("📄")
        
        with col2:
            st.markdown(f"**{content['title']}**")
            st.caption(f"{content.get('author', 'Unknown')}")
            
            # Show content type and match score
            type_badge = content.get('content_type', 'unknown').capitalize()
            score_percent = int(score * 100)
            st.markdown(
                f"<span class='content-type-badge'>{type_badge}</span>"
                f"<span class='similarity-score'>{score_percent}% Match</span>",
                unsafe_allow_html=True
            )
            
            if st.button("View", key=f"view_query_{content_id}", type="secondary"):
                handle_content_click(content_id)
                st.rerun()


def display_content_viewer(content_id: str):
    """Display the selected content item."""
    if not content_id or content_id not in st.session_state.all_discovery_content:
        st.warning("⚠️ Content not found. Please select another item.")
        return
    
    content = st.session_state.all_discovery_content[content_id]
    
    st.markdown("<div class='content-viewer'>", unsafe_allow_html=True)
    
    # Side-by-side layout: Image left, metadata right (compact ratio)
    col_img, col_meta = st.columns([1, 3])
    
    with col_img:
        # Display cover image if available
        if content.get('cover_page'):
            st.image(optimize_image_url(content['cover_page'], width=280), use_container_width=True)
        else:
            st.markdown("### 📄")
    
    with col_meta:
        # Display title
        st.markdown(f"<div class='content-title'>{content['title']}</div>", unsafe_allow_html=True)
        
        # Display author
        if content.get('author'):
            st.markdown(f"<div class='content-author'>By {content['author']}</div>", unsafe_allow_html=True)
        
        # Display category and content type badges
        category = content.get('category', 'Uncategorized')
        content_type = content.get('content_type', 'unknown').capitalize()
        st.markdown(
            f"<span class='content-category'>{category}</span>"
            f"<span class='content-type-badge'>{content_type}</span>",
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_similar_content(target_content_id: str):
    """Calculate and display similar content items."""
    if not target_content_id or target_content_id not in st.session_state.all_discovery_content:
        return
    
    # Find similar content
    similar_items = find_similar_content(
        target_content_id,
        st.session_state.all_discovery_content,
        top_k=5
    )
    
    if not similar_items:
        st.info("No similar content found.")
        return
    
    st.markdown("<div class='similar-header'>✨ Similar Content</div>", unsafe_allow_html=True)
    
    # Display similar items in a grid
    for i in range(0, len(similar_items), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(similar_items):
                content_id, similarity_score = similar_items[i + j]
                content = st.session_state.all_discovery_content[content_id]
                
                with col:
                    # Create a card for each similar item
                    card_col1, card_col2 = st.columns([1, 2])
                    
                    with card_col1:
                        if content.get('cover_page'):
                            st.image(optimize_image_url(content['cover_page'], width=380), use_container_width=True)
                        else:
                            st.markdown("📄")
                    
                    with card_col2:
                        st.markdown(f"**{content['title'][:50]}{'...' if len(content['title']) > 50 else ''}**")
                        st.caption(f"{content.get('author', 'Unknown')}")
                        
                        # Show similarity score
                        score_percent = int(similarity_score * 100)
                        st.markdown(
                            f"<span class='similarity-score'>{score_percent}% Match</span>",
                            unsafe_allow_html=True
                        )
                        
                        if st.button("View", key=f"similar_{content_id}", type="secondary"):
                            handle_content_click(content_id)
                            st.rerun()


def main():
    """Main app logic for discovery page."""
    initialize_discovery_state()
    
    # Check if content is available
    if not st.session_state.all_discovery_content:
        st.error("❌ No content found in database. Please check your MongoDB connection.")
        return
    
    # Display unified search bar with toggle
    display_unified_search_bar()
    
    # Display search results based on mode
    if st.session_state.search_mode == 'title' and st.session_state.search_query:
        display_search_results()
    elif st.session_state.search_mode == 'query' and st.session_state.query_search_input:
        display_query_search_results()
    
    # Display selected content only if not actively searching
    if not st.session_state.search_query and not st.session_state.query_search_input:
        if st.session_state.selected_content_id:
            display_content_viewer(st.session_state.selected_content_id)
            
            # Display similar content
            display_similar_content(st.session_state.selected_content_id)
        else:
            st.info("👆 Use the search bar above to find content, or refresh to see a random item.")


if __name__ == "__main__":
    main()