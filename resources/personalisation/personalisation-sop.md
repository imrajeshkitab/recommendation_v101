# Kitab Personalization & Recommendation System
------

To recommend the right wisdom content—be it bytes, journeys, or books—for each user like Blinkist does, Kitab must be powered by well-designed multi-level metadata + user interaction signals + context-aware data points.

Here’s a breakdown of all key data points we should track and design for.

### **1. Wisdom Content Data (Supply side)**

This is content-level metadata that helps categorize and rank each Byte, Journey, or Book.

**a. Universal Metadata (Applies to all types)**

| Data Point | Description |
| --- | --- |
| `Title` | Display title |
| `Type` | Byte / Journey / Book |
| `Author/Source` | e.g., Bhagavad Gita, Sadhguru, Book name |
| `Estimated Time` | Duration (in minutes/words) |
| `Wisdom Tier` | Beginner, Intermediate, Advanced |
| `Format` | Audio, Text, Visual, Interactive |
| `Language & Tone` | Reflective, Practical, Inspiring, Poetic |

**b. Semantic Metadata**

| Data Point | Description |
| --- | --- |
| `Themes` | e.g. Decision-making, Mindfulness, Detachment, Purpose |
| `Tags` | Freeform topics or values (peace, fear, ego, clarity) |
| `Life Challenges` | e.g. Anxiety, Self-doubt, Relationships |
| `Mood/Energy` | Calm, Active, Reflective, Uplifting |
| `Time of Day` | Best suited for Morning, Evening, Night |
| `Contextual Triggers` | Ideal for breaks, focus moments, emotional lows, etc. |
| `Emotional Outcome` | Intended effect: Peace, Focus, Courage, etc. |
| `Recommended For` | Life stage: Student, Working Adult, Parent, Retired |
| `Spiritual Intensity` | Light, Moderate, Deep |

**c. Content Embeddings *(ML-relevant)***

- BERT-style embeddings of title + summary
- Audio transcript embeddings (for bytes)
- Vector index for similarity search

### 2. User Data (Demand Side)

These help create a dynamic understanding of the user’s wisdom preferences, context, and evolution.

**a. Explicit User Data**

| Data Point | Description |
| --- | --- |
| `Age` | Influences life phase |
| `Gender` | Optional |
| `Marital/Family Status` | Optional, used to recommend contextually relevant content |
| `User Goals` | Selected during onboarding (e.g. “Find inner calm”) |
| `Preferred Tone/Format` | Audio vs Text, Practical vs Reflective |
| `Wisdom Score` | Kitab’s internal progression indicator |
| `Motivational Type` | Explorer, Seeker, Doer, Emotional, Intellectual |

**b. Behavioral Data**

| Data Point | Description |
| --- | --- |
| `Session Time` | When they usually consume content |
| `Completion Rate` | % of bytes/journeys finished |
| `Skips/Drops` | Where and when users bounce |
| `Likes / Bookmarks / Favorites` | Shows affinity |
| `Reflections Written` | Deeper engagement metric |
| `Daily/Weekly Activity Pattern` | Frequency, duration of app usage |
| `Content Revisited` | Indicates strong resonance |

**c. Derived User Features**

- `Wisdom Persona` (e.g., Silent Reflector, Active Seeker, Life Explorer)
- `Topic Affinity` vector (weights per theme/topic)
- `Engagement Vector` (format + tone + challenge preferences)
- `Wisdom Tier` (based on consistency + depth + reflections)
- `Contextual Preference Pattern` (e.g., prefers deep bytes at night)

### 3. Interactions + Contextual Data

| Data Point | Description |
| --- | --- |
| `Current Time of Day` | Recommend short bytes in morning, deep journeys at night |
| `Current Streak` | Use for motivating personalized content (“Keep your journey going”) |
| `Current Energy/Mood` (optional) | If user selects mood (Headspace-style), tune recommendations |
| `Previous Feedback` | “Too deep”, “Not relevant”, “Loved it” → learning loop |
| `Recommendations Clicked` | Indicates recommendation accuracy |
| `Search Queries` | Surface hidden interest themes |

### 4. System Level Data Points

These improve recommendation diversity and ranking.

| Data Point | Description |
| --- | --- |
| `Popularity Score` | Trending or top-rated content |
| `Freshness` | Recently added wisdom bytes |
| `Diversity Index` | To avoid showing similar content repeatedly |
| `Collaborative Interest Score` | What similar users found helpful |

---

### User-to-Content Matching Algorithm

(inspired by Blinkist but adapted for wisdom journeys and bytes)

The algorithm will combine semantic similarity, behavioral feedback, context awareness, and wisdom score progression to recommend the most relevant content.

We’ll use a hybrid matching algorithm that combines:

1. Content Embeddings Similarity
2. Wisdom Score Tier Matching
3. Behavioral Affinity
4. Contextual Filtering
5. Popularity & Diversity Re-ranking

### Step 1: Vector Embeddings

Embed both the user and content in a high-dimensional space using Transformer-based models.

**1.1. Content Embedding (precomputed)**

```python

content_embedding = Encoder([title + summary + tags + challenges + mood])
```

**1.2. User Embedding (dynamically computed)**

```python
user_embedding = Encoder([
    recent likes,
    completed journeys,
    most frequent tags/themes,
    reflection tone,
    preferred energy/mood
])
```

Use `Sentence-BERT`, `MiniLM`, or fine-tuned `BERT` for embedding generation.

### Step 2: Embedding Similarity Score

```python
similarity_score = cosine_similarity(user_embedding, content_embedding)
```

This captures **semantic closeness** between user interests and content meaning.

### Step 3: Wisdom Tier Matching

Each content and user has a `wisdom_tier`: {1: Beginner, 2: Intermediate, 3: Advanced}

```python
wisdom_score_factor = 1 if content_tier == user_tier else 0.5 if abs(content_tier - user_tier) == 1 else 0.1
```

This ensures we match content to user evolution level.

### Step 4: Behavioral Affinity Boost

If the user has interacted with similar content tags/themes:

```python
affinity_boost = Jaccard(user_recent_tags, content_tags)  # Range: 0–1
```

You can also use a weighted average of tag intersections or attention scores from prior usage.

### Step 5: Contextual Filtering

Filter or boost based on current app session context.

```python
if content_time_of_day == user_current_time:
    context_boost = 1.2
else:
    context_boost = 1.0
```

Also apply:

- Mood match (if selected)
- Energy preference match
- Day of week (short bytes on weekdays, journeys on weekends)

### Step 6: Popularity & Diversity Re-Ranking

To avoid filter bubbles and surface crowd favorites:

```python
popularity_score = log(1 + content_completion_count)
diversity_penalty = content_shown_recently_score
```

### Step 7: Final Scoring Function

```python
final_score = (
    0.4 * similarity_score +
    0.2 * wisdom_score_factor +
    0.2 * affinity_boost +
    0.1 * context_boost +
    0.1 * log(1 + popularity_score)
) - diversity_penalty
```

> *You can tune these weights with A/B testing and feedback learning.*
> 

### Output

```json
[
  {
    "content_id": "byte_234",
    "title": "Detach without guilt",
    "type": "byte",
    "score": 0.89
  },
  {
    "content_id": "journey_512",
    "title": "Understanding Dharma in Modern Life",
    "type": "journey",
    "score": 0.85
  }
]
```