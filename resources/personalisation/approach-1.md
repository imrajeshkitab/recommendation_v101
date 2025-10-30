

| Category | Examples | Data Source |
| ----- | ----- | ----- |
| **User Profile** | Age, profession, goals, reading purpose (e.g., productivity, spirituality) | Onboarding questionnaire |
| **Reading Behavior** | Books opened, completion %, time spent, favorite highlights | App usage logs |
| **Engagement Actions** | Likes, saves, shares, skips, comments | App interactions |
| **Contextual Data** | Time of day, reading session length, device type | Behavioral analytics |
| **Semantic Embeddings** | Embeddings of user interests & book ideas | LLM \+ vector database (e.g., Pinecone, Qdrant) |

---

# **Approach 1 — Tag-Based Personalization (Foundational System)**

**Goal:**  
 Deliver immediate, explainable personalization using onboarding data and tagged metadata from book summaries.

## **🧱 Data Requirements**

### **User Profile**

Collected from onboarding & settings:

* Age group

* Parent or not

* Motivations/interests (focus, stress, mindfulness, etc.)

* Preferred reading format (text/audio)

* Preferred session length

### **Content Metadata**

* Title, Author, Summary

* Tags (themes, topics, moods)

* Length (in minutes or words)

* Format (text/audio/visual)

* Popularity, Recency

---

## **⚙️ Implementation Steps**

### **1\. Tag Taxonomy & Mapping**

* Build master taxonomy: `["focus", "mindfulness", "leadership", "habits", "spirituality", "growth", ...]`

* Map content summaries → tags (manual \+ NLP classification)

* Map onboarding inputs → same tags

### **2\. Ranking Score**

Score \= tag overlap \+ popularity \+ recency

score \= 0.5\*tag\_overlap \+ 0.3\*popularity \+ 0.2\*recency

