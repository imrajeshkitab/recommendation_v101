# 🚀 Quick Start Guide

## ⚡ 3 Steps to Run

### 1️⃣ Setup (One-time)

```bash
cd recommendation-poc-app

# Install dependencies
pip install -r requirements.txt

# Load question tags into MongoDB (first time only)
python3 setup_question_tags.py
```

### 2️⃣ Verify

```bash
# Run diagnostics
python3 test_setup.py
```

Expected output:
```
✅ MONGODB_URL found
✅ Connected to MongoDB
📋 Questions found: 9
📚 Published content found: XX
✅ All systems ready!
```

### 3️⃣ Run

```bash
streamlit run app.py
```

Open browser: `http://localhost:8501`

---

## 📝 Environment Setup

Ensure `.env` file exists with:

```
MONGODB_URL=mongodb+srv://your-connection-string
```

---

## 📊 What You Get

- **9 Questions** → User answers progressively
- **Real-time Scoring** → Jaccard similarity after each question
- **Top 10 Recommendations** → Personalized content cards
- **Modern UI** → Netflix-style design
- **Start Over** → Reset and try again

---

## 🎯 Key Features

✅ Single & multiple choice questions  
✅ Progress tracking with visual bar  
✅ Tag accumulation across answers  
✅ Multi-category scoring (8 categories)  
✅ Card-based recommendations grid  
✅ Cover images, titles, authors  
✅ Match percentage display  
✅ Responsive design  

---

## 🔧 Quick Customizations

### Change number of recommendations
`utils/config.py` → `TOP_K_RECOMMENDATIONS = 20`

### Change UI colors
`app.py` → Edit CSS gradient colors

### Modify scoring algorithm
`modules/scoring.py` → Edit `calculate_score()`

### Hide match percentage
`app.py` → Comment out `st.caption(f"Match: {score:.1%}")`

---

## 📚 Full Documentation

- **README.md** - Overview & architecture
- **SETUP.md** - Detailed setup instructions
- **USAGE.md** - Advanced usage & customization
- **IMPLEMENTATION_SUMMARY.md** - Complete implementation details

---

## ❓ Troubleshooting

**Connection Error?**  
→ Check `.env` file has valid `MONGODB_URL`

**No Questions Found?**  
→ Verify collection: `kitab-prod-tables.seed_onboarding_questions`  
→ Run: `python3 setup_question_tags.py`

**No Content Found?**  
→ Verify collection: `kitab-prod-tables.combined`  
→ Check content has `published: true` and `tags` field

**Import Errors?**  
→ Run: `pip install -r requirements.txt`

---

## 🎨 UI Preview

```
┌─────────────────────────────────────────┐
│  Question 1 of 9                        │
│  ████████░░░░░░░░░░░░░░░ 33%           │
│                                         │
│  What is your age group?                │
│                                         │
│  ┌─────────────┐  ┌─────────────┐     │
│  │ 16-25 years │  │ 26-35 years │     │
│  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐     │
│  │ 36-50 years │  │   50+ years │     │
│  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────┘

              ↓  (after 9 questions)  ↓

┌─────────────────────────────────────────┐
│  ✨ Your Personalized Recommendations   │
│     Curated just for you                │
│                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ IMG  │  │ IMG  │  │ IMG  │         │
│  │Title │  │Title │  │Title │         │
│  │85%   │  │82%   │  │79%   │         │
│  └──────┘  └──────┘  └──────┘         │
│  ...                                    │
│                                         │
│         [ 🔄 Start Over ]               │
└─────────────────────────────────────────┘
```

---

## 📊 Tech Stack

- **Frontend**: Streamlit (Python)
- **Database**: MongoDB (kitab-prod-tables)
- **Algorithm**: Jaccard Similarity
- **Styling**: Custom CSS
- **Architecture**: Modular (MVC-like)

---

## 🎓 How It Works

1. User answers questionnaire (9 questions)
2. Tags extracted from each answer
3. Tags mapped to content categories
4. Jaccard similarity calculated for all content
5. Top 10 highest scoring items displayed
6. User can start over for new recommendations

---

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Last Updated**: October 2025

Need help? Check `USAGE.md` or run `python3 test_setup.py`

