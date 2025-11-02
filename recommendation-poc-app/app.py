"""
Personalized Content Recommendation App
Built with Streamlit - Modern UI for questionnaire-based content recommendations
"""

import streamlit as st
from typing import Dict, List, Set
import ast

from modules.db_client import get_db_client
from modules.scoring import calculate_all_content_scores
from utils.config import (
    QUESTION_TAG_MAPPING, 
    TOP_K_RECOMMENDATIONS
)


# Page Configuration
st.set_page_config(
    page_title="Personalized Recommendations",
    page_icon="✨",
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
    
    /* Question container */
    .question-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .question-text {
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .progress-text {
        color: rgba(255,255,255,0.8);
        font-size: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Option buttons */
    .stButton > button {
        width: 100%;
        padding: 1.5rem;
        font-size: 1.1rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        background: white;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    /* Recommendation list item */
    .recommendation-item {
        display: flex;
        align-items: center;
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .recommendation-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* Thumbnail image */
    .recommendation-thumbnail {
        width: 120px;
        height: 120px;
        object-fit: cover;
        border-radius: 8px;
        margin-right: 1.5rem;
        flex-shrink: 0;
    }
    
    /* Content details */
    .recommendation-details {
        flex-grow: 1;
    }
    
    .content-category {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* Recommendations header */
    .recommendations-header {
        text-align: center;
        padding: 2rem 0;
    }
    
    .recommendations-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .recommendations-subtitle {
        font-size: 1.2rem;
        color: #7f8c8d;
    }
    
    /* Preferences section */
    .preferences-container {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .preferences-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .preferences-subtitle {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 1rem;
    }
    
    .question-label {
        font-size: 1rem;
        font-weight: 600;
        color: #34495e;
        margin-bottom: 0.8rem;
        display: block;
    }
    
    .option-group {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
    }
    
    /* Count badge */
    .count-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'user_responses' not in st.session_state:
        st.session_state.user_responses = {}
    
    if 'accumulated_tags' not in st.session_state:
        st.session_state.accumulated_tags = {}
    
    if 'content_scores' not in st.session_state:
        st.session_state.content_scores = {}
    
    if 'questions' not in st.session_state:
        db_client = get_db_client()
        st.session_state.questions = db_client.get_questions()
    
    if 'all_content' not in st.session_state:
        db_client = get_db_client()
        st.session_state.all_content = db_client.get_all_content()
    
    if 'current_selection' not in st.session_state:
        st.session_state.current_selection = set()
    
    if 'show_preferences' not in st.session_state:
        st.session_state.show_preferences = False
    
    if 'temp_responses' not in st.session_state:
        st.session_state.temp_responses = {}


def optimize_image_url(url: str, width: int = 380, resize: str = "contain") -> str:
    """
    Optimize Supabase image URL using the render/image endpoint with transformation parameters.
    
    Transforms:
    - /storage/v1/object/public/... → /storage/v1/render/image/public/...
    - Adds query params: ?width=380&resize=contain
    
    Args:
        url: Original image URL
        width: Desired width in pixels
        resize: Resize mode (contain, cover, fill)
    
    Returns:
        Optimized URL with render endpoint and query parameters
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


def parse_tags_from_csv_format(tags_str: str) -> List[str]:
    """
    Parse tags from CSV format string representation of list.
    Example: '["tag1", "tag2", "tag3"]' -> ["tag1", "tag2", "tag3"]
    """
    if not tags_str or tags_str == '[]':
        return []
    
    try:
        # Use ast.literal_eval to safely parse string representation of list
        return ast.literal_eval(tags_str)
    except:
        # Fallback: try to parse as JSON
        try:
            import json
            return json.loads(tags_str)
        except:
            return []


def get_tags_for_option(question: Dict, option_number: str) -> List[str]:
    """Extract tags for a given option from question data."""
    option_tags = question.get('option_tags', {})
    
    if isinstance(option_tags, dict) and option_number in option_tags:
        tags = option_tags[option_number]
        if isinstance(tags, list):
            return tags
        elif isinstance(tags, str):
            return parse_tags_from_csv_format(tags)
    
    return []


def update_user_tags(question: Dict, selected_options: Set[str]):
    """Update accumulated user tags based on selected options."""
    sequence = question.get('sequence')
    tag_field = QUESTION_TAG_MAPPING.get(sequence)
    
    # Skip if no mapping for this question
    if tag_field is None:
        return
    
    # Collect all tags from selected options
    all_tags = []
    for option_num in selected_options:
        tags = get_tags_for_option(question, option_num)
        all_tags.extend(tags)
    
    # Update accumulated tags
    if tag_field not in st.session_state.accumulated_tags:
        st.session_state.accumulated_tags[tag_field] = []
    
    st.session_state.accumulated_tags[tag_field].extend(all_tags)
    
    # Recalculate scores for all content
    st.session_state.content_scores = calculate_all_content_scores(
        st.session_state.accumulated_tags,
        st.session_state.all_content
    )


def recalculate_scores_from_responses():
    """Recalculate all scores from scratch based on current responses."""
    # Reset accumulated tags
    st.session_state.accumulated_tags = {}
    
    # Reprocess all responses
    for sequence, selected_options in st.session_state.user_responses.items():
        # Find the question
        question = next((q for q in st.session_state.questions if q['sequence'] == sequence), None)
        if question:
            update_user_tags(question, set(selected_options))


def display_question(question: Dict, question_index: int):
    """Display a single question with options."""
    total_questions = len(st.session_state.questions)
    
    # Question container with gradient background
    st.markdown(f"""
    <div class="question-container">
        <div class="progress-text">Question {question_index + 1} of {total_questions}</div>
        <div class="question-text">{question['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress = (question_index) / total_questions
    st.progress(progress)
    
    st.markdown("---")
    
    # Display options
    options = question.get('options', {})
    question_type = question.get('type', 'single_choice')
    
    # Handle multiple choice
    if question_type == 'multiple_choice':
        st.markdown("### 📝 Select all that apply:")
        
        cols = st.columns(2)
        for idx, (option_num, option_text) in enumerate(options.items()):
            with cols[idx % 2]:
                if st.checkbox(option_text, key=f"q{question_index}_option_{option_num}"):
                    st.session_state.current_selection.add(option_num)
                elif option_num in st.session_state.current_selection:
                    st.session_state.current_selection.remove(option_num)
    
    # Handle single choice
    else:
        st.markdown("### 📝 Choose one:")
        
        cols = st.columns(2)
        for idx, (option_num, option_text) in enumerate(options.items()):
            with cols[idx % 2]:
                if st.button(option_text, key=f"q{question_index}_option_{option_num}", use_container_width=True):
                    st.session_state.current_selection = {option_num}
                    handle_next_question(question)
                    st.rerun()
    
    # Next button for multiple choice questions
    if question_type == 'multiple_choice':
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Next →", 
                        disabled=len(st.session_state.current_selection) == 0,
                        use_container_width=True,
                        type="primary"):
                handle_next_question(question)
                st.rerun()


def handle_next_question(question: Dict):
    """Handle moving to next question and updating scores."""
    # Store response
    st.session_state.user_responses[question['sequence']] = list(st.session_state.current_selection)
    
    # Update tags and scores
    update_user_tags(question, st.session_state.current_selection)
    
    # Clear selection
    st.session_state.current_selection = set()
    
    # Move to next question
    st.session_state.current_question += 1


def display_preferences_editor():
    """Display expandable preferences editor."""
    st.markdown("""
    <div class="preferences-container">
        <div class="preferences-title">🎯 Your Preferences</div>
        <div class="preferences-subtitle">Click to modify your answers and update recommendations</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle button
    if st.button("⚙️ Modify Preferences" if not st.session_state.show_preferences else "✕ Close Preferences", 
                 use_container_width=False):
        st.session_state.show_preferences = not st.session_state.show_preferences
        if st.session_state.show_preferences:
            # Initialize temp responses with current responses
            st.session_state.temp_responses = st.session_state.user_responses.copy()
        st.rerun()
    
    # Show preferences form if expanded
    if st.session_state.show_preferences:
        st.markdown("---")
        
        # Initialize temp_responses if not exists
        if not st.session_state.temp_responses:
            st.session_state.temp_responses = st.session_state.user_responses.copy()
        
        # Display all questions with current selections
        for question in st.session_state.questions:
            sequence = question['sequence']
            st.markdown(f"<div class='option-group'>", unsafe_allow_html=True)
            st.markdown(f"<span class='question-label'>Q{sequence}: {question['question']}</span>", 
                       unsafe_allow_html=True)
            
            options = question.get('options', {})
            question_type = question.get('type', 'single_choice')
            current_selections = st.session_state.temp_responses.get(sequence, [])
            
            if question_type == 'multiple_choice':
                # Multiple choice with checkboxes
                cols = st.columns(2)
                new_selections = []
                for idx, (option_num, option_text) in enumerate(options.items()):
                    with cols[idx % 2]:
                        checked = st.checkbox(
                            option_text,
                            value=option_num in current_selections,
                            key=f"pref_q{sequence}_opt_{option_num}"
                        )
                        if checked:
                            new_selections.append(option_num)
                
                st.session_state.temp_responses[sequence] = new_selections
            else:
                # Single choice with radio buttons
                options_list = list(options.items())
                option_labels = [text for _, text in options_list]
                
                # Find current selection index
                current_index = 0
                if current_selections:
                    for idx, (opt_num, _) in enumerate(options_list):
                        if opt_num in current_selections:
                            current_index = idx
                            break
                
                selected_label = st.radio(
                    "Select one:",
                    option_labels,
                    index=current_index,
                    key=f"pref_q{sequence}_radio",
                    label_visibility="collapsed"
                )
                
                # Find the option number for selected label
                for opt_num, opt_text in options_list:
                    if opt_text == selected_label:
                        st.session_state.temp_responses[sequence] = [opt_num]
                        break
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✓ Update Recommendations", use_container_width=True):
                # Apply temp responses to actual responses
                st.session_state.user_responses = st.session_state.temp_responses.copy()
                # Recalculate all scores
                recalculate_scores_from_responses()
                st.session_state.show_preferences = False
                st.rerun()
        
        with col2:
            if st.button("✕ Cancel", use_container_width=True):
                st.session_state.show_preferences = False
                st.session_state.temp_responses = {}
                st.rerun()


def display_recommendations():
    """Display final recommendations."""
    st.markdown("""
    <div class="recommendations-header">
        <div class="recommendations-title">✨ Your Personalized Recommendations</div>
        <div class="recommendations-subtitle">Curated just for you based on your preferences</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display preferences editor
    display_preferences_editor()
    
    st.markdown("---")
    
    # Sort content by score
    sorted_content = sorted(
        st.session_state.content_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:TOP_K_RECOMMENDATIONS]
    
    # Display count
    st.markdown(f"### 📚 Top {len(sorted_content)} Recommendations for You")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display as vertical list
    for i, (content_id, score) in enumerate(sorted_content):
        content = st.session_state.all_content[content_id]
        
        # Create horizontal layout: image | details
        col_img, col_details = st.columns([1, 4])
        
        with col_img:
            if content['cover_page']:
                st.image(optimize_image_url(content['cover_page']), use_container_width=True)
        
        with col_details:
            st.markdown(f"### {content['title']}")
            st.markdown(f"**{content.get('author', '')}**")
            st.markdown(f"<span class='content-category'>{content.get('category', '')}</span>", unsafe_allow_html=True)
        
        # Add spacing between items
        if i < len(sorted_content) - 1:
            st.markdown("---")
    
    # Start over button
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Start Over", use_container_width=True, type="secondary"):
            # Reset session state
            for key in ['current_question', 'user_responses', 'accumulated_tags', 
                       'content_scores', 'current_selection', 'show_preferences', 'temp_responses']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def main():
    """Main app logic."""
    initialize_session_state()
    
    # Check if we have questions and content
    if not st.session_state.questions:
        st.error("❌ No questions found in database. Please check your MongoDB connection.")
        return
    
    if not st.session_state.all_content:
        st.error("❌ No content found in database. Please check your MongoDB connection.")
        return
    
    # Determine which page to show
    total_questions = len(st.session_state.questions)
    current_idx = st.session_state.current_question
    
    if current_idx < total_questions:
        # Show question
        question = st.session_state.questions[current_idx]
        display_question(question, current_idx)
    else:
        # Show recommendations
        display_recommendations()


if __name__ == "__main__":
    main()