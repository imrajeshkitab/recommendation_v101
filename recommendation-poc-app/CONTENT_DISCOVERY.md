# Content Discovery Page

## Overview

A new Streamlit page that allows users to explore content through search and similarity-based recommendations using Jaccard similarity on content tags.

## Features

### 1. Random Content on Load
- Displays a randomly selected content item when the page first loads
- Shows content from any of the three collections (bytes, summaries, journeys)

### 2. Search Functionality
- **Search Bar**: Search content by title (case-insensitive)
- **Multi-Filter Support**: Filter by content types
  - Bytes
  - Summaries  
  - Journeys
- **Text Search**: Enter keywords to find matching content
- **Random Discovery**: Leave search empty and click Search to get random content from selected filters
- **Results Limit**: Returns up to 10 results
- **Clickable Results**: Each result can be clicked to view full content

### 3. Content Display
The main content viewer shows:
- Cover image (optimized for performance)
- Title
- Author
- Category badge
- Content type badge

### 4. Similarity-Based Recommendations
- Calculates Jaccard similarity between selected content and all other content
- Displays top 5 most similar items
- Shows similarity score as a percentage
- Each similar item is clickable to navigate

### 5. Seamless Navigation
- Click on any search result or similar content to load it
- Automatically updates similar content recommendations
- Search state clears when navigating to new content

## Technical Implementation

### Files Created/Modified

**New Files:**
1. `modules/content_similarity.py` - Content-to-content similarity calculation
2. `pages/1_🔍_Discover.py` - Main discovery page

**Modified Files:**
1. `modules/db_client.py` - Added three new methods:
   - `get_all_content_for_discovery()` - Fetches from all 3 collections
   - `search_content_by_title(query, filters)` - Search with filters
   - `get_content_by_id(content_id, content_type)` - Retrieve specific content

### Database Collections

Queries three collections from `kitab-prod-tables` database:
- `bytes` - Bite-sized content
- `summaries` - Book/content summaries  
- `journeys` - Learning journeys

### Similarity Algorithm

Uses Jaccard similarity from `modules/scoring.py`:
- Compares 8 tag categories between content items:
  - life_stage_age
  - life_stage_relationship
  - life_stage_parenting
  - primary_need
  - motivation_driver
  - cognitive_style
  - content_depth
  - learning_style
- Returns average similarity across all categories
- Scores range from 0.0 (no similarity) to 1.0 (identical tags)

### UI Design

Consistent with main app styling:
- Gradient headers (purple theme)
- Card-based layouts with hover effects
- Modern button styling
- Responsive column layouts
- Image optimization for performance

## Usage

### Running the App

```bash
cd recommendation-poc-app
streamlit run app.py
```

The discovery page will be accessible from the sidebar navigation as "🔍 Discover".

### User Flow

1. **Initial Load**: User sees a random content item with its similar recommendations
2. **Search**: User can search by title and filter by content type
3. **Explore**: User clicks on search results or similar items to explore
4. **Discover**: Each new content shows 5 similar items, creating an exploration journey

## Session State Management

The page maintains the following session state variables:
- `all_discovery_content` - Cached content from all collections
- `selected_content_id` - Currently displayed content
- `search_query` - Current search term
- `search_results` - Current search results
- `active_filters` - Selected content type filters

## Performance Optimizations

1. **Caching**: Uses `@st.cache_resource` for database client
2. **Image Optimization**: Transforms Supabase images with width/resize parameters
3. **Result Limiting**: Caps search results at 10 items
4. **Lazy Loading**: Only calculates similarity when displaying content

## Future Enhancements

Potential improvements:
- Add pagination for search results
- Include content text in search (currently title only)
- Filter by category or author
- Save favorite content
- View history
- Export recommendations

