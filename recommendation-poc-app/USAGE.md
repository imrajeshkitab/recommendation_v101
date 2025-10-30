# Usage Guide

## Running the App

### Basic Usage

```bash
cd recommendation-poc-app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### With Custom Port

```bash
streamlit run app.py --server.port 8080
```

### Production Mode

```bash
streamlit run app.py --server.headless true
```

## User Journey

### Step 1: Welcome Screen
- User sees the first question with a gradient header
- Progress indicator shows "Question 1 of 9"
- Progress bar displays completion percentage

### Step 2: Answer Questions
- **Single Choice**: Click any option to automatically proceed
- **Multiple Choice**: Select multiple options, then click "Next"
- User cannot proceed without making a selection

### Step 3: Real-time Scoring
- After each question, tags are extracted from selections
- Tags are mapped to content tag categories
- Jaccard similarity scores are recalculated for ALL content
- Process is invisible to user (happens in background)

### Step 4: View Recommendations
- After question 9, recommendations page displays
- Shows top 10 content items in a card grid (3 columns)
- Each card displays:
  - Cover image
  - Title
  - Author
  - Category badge
  - Match percentage
- "Start Over" button resets the session

## Understanding the Scoring

### Jaccard Similarity Formula

```
Score = |User Tags ∩ Content Tags| / |User Tags ∪ Content Tags|
```

**Example:**

User tags: `["peace", "balance", "growth"]`
Content tags: `["peace", "growth", "mindfulness"]`

- Intersection: `["peace", "growth"]` = 2 tags
- Union: `["peace", "balance", "growth", "mindfulness"]` = 4 tags
- Jaccard Score: `2/4 = 0.5 = 50%`

### Multi-Category Scoring

The app calculates scores across 8 tag categories:

1. **life_stage_age**: Age-related tags
2. **life_stage_relationship**: Relationship status tags
3. **life_stage_parenting**: Parenting tags
4. **primary_need**: Core needs and goals
5. **motivation_driver**: What drives the user
6. **cognitive_style**: Thinking and decision-making style
7. **content_depth**: Time commitment preference
8. **learning_style**: Learning approach preference

**Final Score** = Average of Jaccard scores across all categories

### Example Calculation

**User Profile (from answers):**
```python
{
  "life_stage_age": ["young adult", "Gen Z"],
  "primary_need": ["peace", "balance", "growth"],
  "motivation_driver": ["inner peace"],
  "cognitive_style": ["values-driven"],
  "content_depth": ["quick learner"],
  "learning_style": ["reflective"]
}
```

**Content Item Tags:**
```python
{
  "life_stage_age": [],
  "primary_need": ["peace", "growth", "mindfulness"],
  "motivation_driver": ["inner peace", "clarity"],
  "cognitive_style": ["values-driven", "emotional"],
  "content_depth": ["quick learner", "efficient"],
  "learning_style": ["reflective", "practical"]
}
```

**Category Scores:**
- life_stage_age: 0.0 (no content tags)
- primary_need: 2/4 = 0.50
- motivation_driver: 1/2 = 0.50
- cognitive_style: 1/2 = 0.50
- content_depth: 1/2 = 0.50
- learning_style: 1/2 = 0.50

**Final Score:** (0.0 + 0.50 + 0.50 + 0.50 + 0.50 + 0.50) / 6 = **0.42** (42%)

## Customization Options

### 1. Change Number of Recommendations

Edit `utils/config.py`:

```python
TOP_K_RECOMMENDATIONS = 20  # Show top 20 instead of 10
```

### 2. Modify UI Colors

Edit CSS in `app.py`:

```python
# Change gradient colors
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# Change to your brand colors
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### 3. Add Score Threshold

Edit `app.py` in `display_recommendations()`:

```python
# Only show recommendations with score > 0.3
sorted_content = [
    (id, score) for id, score in sorted_content
    if score > 0.3
][:TOP_K_RECOMMENDATIONS]
```

### 4. Hide Match Percentage

Edit `app.py`, comment out this line:

```python
# st.caption(f"Match: {score:.1%}")
```

### 5. Change Grid Layout

Edit `app.py`:

```python
cols_per_row = 4  # Show 4 columns instead of 3
```

## Advanced Features

### Session State Variables

You can access these in your custom code:

```python
st.session_state.current_question      # Current question index (0-8)
st.session_state.user_responses        # Dict of {sequence: [options]}
st.session_state.accumulated_tags      # Dict of {category: [tags]}
st.session_state.content_scores        # Dict of {content_id: score}
st.session_state.all_content          # Dict of all content data
st.session_state.questions            # List of all questions
```

### Add Analytics

Track user behavior:

```python
# In app.py, add after each question submission
import json

with open('analytics.jsonl', 'a') as f:
    event = {
        'timestamp': datetime.now().isoformat(),
        'question': question['sequence'],
        'response': list(st.session_state.current_selection)
    }
    f.write(json.dumps(event) + '\n')
```

### Export Recommendations

Add export button in `display_recommendations()`:

```python
import json

recommendations_data = [
    {
        'title': st.session_state.all_content[content_id]['title'],
        'score': score
    }
    for content_id, score in sorted_content
]

if st.download_button(
    "📥 Download Recommendations",
    data=json.dumps(recommendations_data, indent=2),
    file_name="my_recommendations.json",
    mime="application/json"
):
    st.success("Downloaded!")
```

## Debugging

### Enable Debug Mode

Add at the top of `app.py`:

```python
DEBUG = True

if DEBUG:
    st.sidebar.title("Debug Info")
    st.sidebar.write("Session State:", st.session_state)
    st.sidebar.write("Current Question:", st.session_state.current_question)
    st.sidebar.write("Accumulated Tags:", st.session_state.accumulated_tags)
    st.sidebar.write("Top 5 Scores:", 
        sorted(st.session_state.content_scores.items(), 
               key=lambda x: x[1], reverse=True)[:5])
```

### View Raw Data

```python
# In display_recommendations(), add:
with st.expander("🔍 View Raw Scores"):
    import pandas as pd
    scores_df = pd.DataFrame([
        {
            'Content': st.session_state.all_content[cid]['title'],
            'Score': score
        }
        for cid, score in sorted(
            st.session_state.content_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
    ])
    st.dataframe(scores_df)
```

### Log to File

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Use throughout app.py
logging.info(f"Question {question['sequence']} answered")
logging.info(f"Tags accumulated: {len(st.session_state.accumulated_tags)}")
```

## Performance Tips

### 1. Cache Database Queries

Already implemented with `@st.cache_resource` decorator in `db_client.py`

### 2. Optimize Content Loading

Load only necessary fields:

```python
# In db_client.py, get_all_content()
content_docs = list(collection.find(
    {'published': True},
    {
        'title': 1,
        'cover_page': 1,
        'tags': 1,
        '_id': 1
        # Don't load 'content', 'audio', etc.
    }
))
```

### 3. Lazy Load Images

Add lazy loading to images:

```python
st.image(content['cover_page'], use_column_width=True)
```

## Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Add secrets in dashboard:
   ```
   MONGODB_URL = "your-connection-string"
   ```
5. Deploy!

### Deploy with Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

Build and run:

```bash
docker build -t recommendation-app .
docker run -p 8501:8501 --env-file .env recommendation-app
```

## FAQ

**Q: Can I use a different similarity algorithm?**  
A: Yes! Edit `modules/scoring.py` and modify `calculate_score()`. The function signature should remain the same for compatibility.

**Q: How do I add more questions?**  
A: Add questions to MongoDB with sequential `sequence` numbers. Update `QUESTION_TAG_MAPPING` in `config.py`.

**Q: Can I filter recommendations by category?**  
A: Yes! Add a selectbox in `display_recommendations()` and filter the sorted_content list.

**Q: How do I change the question order?**  
A: Update the `sequence` field in MongoDB questions. The app sorts by sequence automatically.

**Q: Can users skip questions?**  
A: Currently no, but you can add a "Skip" button that proceeds without updating tags.

