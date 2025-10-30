# Setup Guide

## Quick Start

### 1. Configure MongoDB Connection

**For Local Development:**

Create a `.env` file in the `recommendation-poc-app` directory with your MongoDB connection:

```bash
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority
```

**For Streamlit Cloud Deployment:**

The app will automatically use Streamlit secrets. No `.env` file needed. Configure in your app settings:

```toml
MONGODB_URL = "mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority"
```

### 2. Install Dependencies

```bash
cd recommendation-poc-app
pip install -r requirements.txt
```

### 3. Load Question Tags (First Time Only)

If your MongoDB questions don't have `option_tags` yet, run this script to populate them from the CSV:

```bash
python setup_question_tags.py
```

This will:
- Read tags from `../database/tables/questionnaire-tags.csv`
- Add `option_tags` field to each question in MongoDB
- Display confirmation and sample data

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Verification Checklist

Before running the app, verify:

- [ ] `.env` file created with valid `MONGODB_URL`
- [ ] MongoDB connection is accessible (check IP whitelist on Atlas)
- [ ] Database `kitab-prod-tables` exists
- [ ] Collection `seed_onboarding_questions` exists with 9 questions
- [ ] Collection `combined` exists with content and `tags` field
- [ ] Questions have `option_tags` field populated
- [ ] Content has `published: true` field

## Test MongoDB Connection

You can test your connection with this Python snippet:

```python
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URL'))

# Test connection
client.admin.command('ping')
print("✅ Connected to MongoDB!")

# Check collections
db = client['kitab-prod-tables']
print(f"Questions: {db.seed_onboarding_questions.count_documents({})}")
print(f"Content: {db.combined.count_documents({})}")
```

## Troubleshooting

### Import Error: No module named 'streamlit'

```bash
pip install -r requirements.txt
```

### Connection Error: MONGODB_URL not found

Create `.env` file in `recommendation-poc-app/` directory (not root)

### No Questions Found

- Check collection name is `seed_onboarding_questions`
- Verify questions have `sequence` field (1-9)
- Run `setup_question_tags.py` to add `option_tags`

### No Content Found

- Check collection name is `combined`
- Verify content has `published: true`
- Verify content has `tags` field with tag categories

## Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| MONGODB_URL | MongoDB connection string | Yes | `mongodb+srv://...` |

## MongoDB Collections Structure

### seed_onboarding_questions

Required fields:
- `question` (string): Question text
- `type` (string): "single_choice" or "multiple_choice"
- `sequence` (int): 1-9
- `options` (object): `{"1": "Option 1", "2": "Option 2"}`
- `option_tags` (object): `{"1": ["tag1", "tag2"], "2": ["tag3"]}`

### combined

Required fields:
- `title` (string): Content title
- `cover_page` (string): Image URL
- `author` (string): Author name
- `category` (string): Content category
- `published` (boolean): Must be `true`
- `tags` (object): Tag categories with arrays of tags

Example tags structure:
```json
{
  "life_stage_age": ["young adult", "Gen Z"],
  "primary_need": ["personal growth"],
  "motivation_driver": ["inner peace"],
  "cognitive_style": ["values-driven"],
  "content_depth": ["quick learner"],
  "learning_style": ["reflective"]
}
```

