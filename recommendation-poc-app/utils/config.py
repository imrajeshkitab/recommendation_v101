import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv('MONGODB_URL')
DATABASE_NAME = 'kitab-prod-tables'
QUESTIONS_COLLECTION = 'seed_onboarding_questions'
CONTENT_COLLECTION = 'combined'

# App Configuration
TOP_K_RECOMMENDATIONS = 10

# Question to Tag Field Mapping
# Maps question sequence to the corresponding content tag field
QUESTION_TAG_MAPPING = {
    1: 'life_stage_age',           # Q1: What is your age group?
    2: None,                        # Q2: What's your gender? (no mapping)
    3: 'life_stage_relationship',   # Q3: What's your relationship status?
    4: 'life_stage_parenting',      # Q4: Do you have kids?
    5: 'primary_need',              # Q5: What's on your mind these days?
    6: 'motivation_driver',         # Q6: What motivates you the most right now?
    7: 'cognitive_style',           # Q7: How would you relate the following with yourself?
    8: 'content_depth',             # Q8: How much time do you want to spend daily on yourself?
    9: 'learning_style'             # Q9: Choose your learning style
}

# Tag categories for scoring
TAG_CATEGORIES = [
    'life_stage_age',
    'life_stage_relationship',
    'life_stage_parenting',
    'primary_need',
    'motivation_driver',
    'cognitive_style',
    'content_depth',
    'learning_style'
]

