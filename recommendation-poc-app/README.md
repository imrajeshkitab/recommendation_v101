# Personalized Content Recommendation App

A modern Streamlit application that provides personalized content recommendations based on user questionnaire responses using Jaccard similarity scoring.

## Features

- **Interactive Questionnaire Flow**: Displays questions one at a time with single-select and multi-select options
- **Real-time Score Calculation**: Updates content scores after each question using Jaccard similarity
- **Modern UI**: Netflix/YouTube-style card layout for recommendations
- **MongoDB Integration**: Fetches questions and content from MongoDB collections
- **Modular Architecture**: Easy to update scoring algorithms

## Architecture

```
recommendation-poc-app/
├── app.py                      # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── db_client.py           # MongoDB operations
│   └── scoring.py             # Jaccard similarity algorithm
├── utils/
│   └── config.py              # Configuration and constants
├── archives/
│   ├── sample_content.json
│   └── sample_questionnaire.json
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd recommendation-poc-app
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**Option A: Local Development (using .env file)**

Create a `.env` file in the `recommendation-poc-app` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your MongoDB connection string:

```
MONGODB_URL=mongodb+srv://your-connection-string
```

**Option B: Streamlit Cloud Deployment (using secrets)**

The app automatically detects and uses Streamlit secrets when `.env` is not available. In your Streamlit Cloud dashboard, add:

```toml
MONGODB_URL = "mongodb+srv://your-connection-string"
```

### 3. Verify MongoDB Collections

Ensure your MongoDB database (`kitab-prod-tables`) has:
- Collection: `seed_onboarding_questions` with `option_tags` field
- Collection: `combined` with `tags` field

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## How It Works

### Question-to-Tag Mapping

| Question # | Topic | Tag Field |
|------------|-------|-----------|
| Q1 | Age group | `life_stage_age` |
| Q2 | Gender | (no mapping) |
| Q3 | Relationship status | `life_stage_relationship` |
| Q4 | Kids | `life_stage_parenting` |
| Q5 | What's on mind | `primary_need` |
| Q6 | Motivation | `motivation_driver` |
| Q7 | Cognitive style | `cognitive_style` |
| Q8 | Time preference | `content_depth` |
| Q9 | Learning style | `learning_style` |

### Scoring Algorithm

The app uses **Jaccard similarity** to match user preferences with content:

```
Jaccard Similarity = |A ∩ B| / |A ∪ B|
```

For each content item:
1. Calculate Jaccard similarity for each tag category
2. Average across all categories
3. Rank content by final score
4. Display top 10 recommendations

### User Flow

1. User answers 9 onboarding questions
2. After each answer, tags are accumulated
3. Scores are recalculated for all content in real-time
4. After the final question, top 10 recommendations are displayed
5. User can start over to get new recommendations

## Customization

### Update Scoring Algorithm

The scoring algorithm is isolated in `modules/scoring.py`. To use a different algorithm:

1. Modify `calculate_score()` function
2. Keep the same function signature for compatibility
3. Options: cosine similarity, weighted scoring, semantic similarity, etc.

### Adjust Number of Recommendations

In `utils/config.py`, change:

```python
TOP_K_RECOMMENDATIONS = 10  # Change to desired number
```

### Customize UI Styling

Modify the CSS in `app.py` under the `st.markdown()` section with `<style>` tags.

## Data Structure Examples

### Question Document (MongoDB)

```json
{
  "question": "What is your age group?",
  "type": "single_choice",
  "sequence": 1,
  "options": {
    "1": "16-25 years",
    "2": "26-35 years"
  },
  "option_tags": {
    "1": ["young adult", "Gen Z"],
    "2": ["millennials", "young professional"]
  }
}
```

### Content Document (MongoDB)

```json
{
  "title": "Recovery is Rebirth",
  "cover_page": "https://...",
  "author": "DR YVES BENHAMOU",
  "category": "Personal Development",
  "published": true,
  "tags": {
    "life_stage_age": [],
    "primary_need": ["personal growth", "peace"],
    "motivation_driver": ["inner peace", "self-discovery"],
    "cognitive_style": ["values-driven", "emotional"],
    "content_depth": ["busy", "quick learner"],
    "learning_style": ["reflective", "practical"]
  }
}
```

## Troubleshooting

### Connection Error
- Verify `MONGODB_URL` in `.env` file
- Check MongoDB Atlas whitelist (allow your IP)
- Test connection with MongoDB Compass

### No Questions/Content Found
- Verify collection names in `utils/config.py`
- Check that `published: true` for content
- Ensure `option_tags` field exists in questions

### Styling Issues
- Clear browser cache
- Try incognito/private mode
- Check Streamlit version compatibility

## Future Enhancements

- [ ] Add user authentication
- [ ] Store recommendation history
- [ ] A/B test different scoring algorithms
- [ ] Add content filtering options
- [ ] Export recommendations
- [ ] Add feedback mechanism

## License

MIT

