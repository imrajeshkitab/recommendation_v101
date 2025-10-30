"""
Content Discovery Page
Explore content through search and similarity-based recommendations
"""

import streamlit as st
import random
from typing import Dict, List, Optional

from modules.db_client import get_db_client
from modules.content_similarity import find_similar_content


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
        padding: 2rem;
    }
    
    /* Search container */
    .search-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .search-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
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
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .content-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }
    
    .content-author {
        font-size: 1rem;
        color: #7f8c8d;
        margin-bottom: 0.8rem;
    }
    
    .content-category {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .content-type-badge {
        display: inline-block;
        background: #e8f4f8;
        color: #2980b9;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-left: 0.5rem;
    }
    
    /* Similar content section */
    .similar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }
    
    /* Search result item */
    .search-result {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
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
</style>
""", unsafe_allow_html=True)


def optimize_image_url(url: str, width: int = 200, resize: str = "contain") -> str:
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


def handle_content_click(content_id: str):
    """Handle click on a content item to display it."""
    st.session_state.selected_content_id = content_id
    st.session_state.search_query = ""
    st.session_state.search_results = {}


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


def display_search_bar():
    """Display search bar with filter options."""
    st.markdown("""
    <div class="search-container">
        <div class="search-title">🔍 Discover Content</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Search input and filters in columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search by title",
            placeholder="Enter search term...",
            label_visibility="collapsed",
            key="search_input"
        )
    
    with col2:
        if st.button("🔍 Search", use_container_width=True, type="primary", key="search_btn"):
            if search_query.strip():
                # Perform text search
                st.session_state.search_query = search_query
                perform_search()
                st.rerun()
            else:
                # Show random content from selected filters
                if st.session_state.active_filters:
                    random_content_id = get_random_content_from_filters(st.session_state.active_filters)
                    if random_content_id:
                        st.session_state.selected_content_id = random_content_id
                        st.session_state.search_query = ""
                        st.session_state.search_results = {}
                        st.rerun()
                    else:
                        st.warning("No content found in selected filters")
                else:
                    st.warning("Please select at least one filter or enter a search term")
    
    # Filter checkboxes
    st.markdown("**Filter by content type:**")
    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 3])
    
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
    
    # Hint text
    st.caption("💡 Tip: Leave search empty and click Search to get random content from selected filters")


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
        col_result, col_clear = st.columns([4, 1])
        with col_result:
            if st.session_state.search_results:
                st.markdown(f"### 🔎 Search Results ({len(st.session_state.search_results)} found)")
            else:
                st.info(f"🔍 No results found for '{st.session_state.search_query}'. Try different keywords or filters.")
        
        with col_clear:
            if st.button("✕ Clear Search", key="clear_search", use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.search_results = {}
                st.rerun()
    
    if not st.session_state.search_results:
        return
    
    st.markdown("---")
    
    # Display results in a scrollable area
    for content_id, content in st.session_state.search_results.items():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if content.get('cover_page'):
                st.image(optimize_image_url(content['cover_page'], width=100), use_container_width=True)
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
        
        st.markdown("---")


def display_content_viewer(content_id: str):
    """Display the selected content item."""
    if not content_id or content_id not in st.session_state.all_discovery_content:
        st.warning("⚠️ Content not found. Please select another item.")
        return
    
    content = st.session_state.all_discovery_content[content_id]
    
    st.markdown("<div class='content-viewer'>", unsafe_allow_html=True)
    
    # Side-by-side layout: Image left, metadata right
    col_img, col_meta = st.columns([1, 2])
    
    with col_img:
        # Display cover image if available
        if content.get('cover_page'):
            st.image(optimize_image_url(content['cover_page'], width=300), use_container_width=True)
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
                            st.image(optimize_image_url(content['cover_page'], width=100), use_container_width=True)
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
                    
                    st.markdown("")  # Small spacing


def main():
    """Main app logic for discovery page."""
    initialize_discovery_state()
    
    # Check if content is available
    if not st.session_state.all_discovery_content:
        st.error("❌ No content found in database. Please check your MongoDB connection.")
        return
    
    # Display search bar
    display_search_bar()
    
    # Display search results if searching (even if empty to show "no results" message)
    if st.session_state.search_query:
        display_search_results()
    
    # Show separator if not searching or if search has results
    if not st.session_state.search_query or st.session_state.search_results:
        st.markdown("---")
    
    # Display selected content only if not actively searching
    if not st.session_state.search_query and st.session_state.selected_content_id:
        display_content_viewer(st.session_state.selected_content_id)
        
        # Display similar content
        display_similar_content(st.session_state.selected_content_id)
    elif not st.session_state.search_query:
        st.info("👆 Use the search bar above to find content, or refresh to see a random item.")


if __name__ == "__main__":
    main()

