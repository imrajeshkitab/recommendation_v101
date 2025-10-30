# Changelog

## [1.1.0] - 2025-10-30

### 🐛 Bug Fixes

#### Fixed: Checkbox State Persisting Across Questions

**Issue:** When navigating from one question to another, checkboxes/selections from the previous question would appear pre-selected in the new question if they were at the same UI position.

**Root Cause:** Widget keys were not unique across questions. Both Question 5 and Question 6 used keys like `option_1`, `option_2`, causing Streamlit to reuse widget state.

**Solution:** Added question index to widget keys to ensure uniqueness.

**Changes:**
- Modified checkbox keys: `option_{num}` → `q{question_index}_option_{num}`
- Modified button keys: `option_{num}` → `q{question_index}_option_{num}`
- Files changed: `app.py` (lines 267, 279)

**Impact:** 
- ✅ Each question now starts with clean state
- ✅ No UI glitches or pre-selected options
- ✅ Better user experience
- ✅ No breaking changes

**Details:** See `BUGFIX_CHECKBOX_STATE.md`

---

## [1.0.0] - 2025-10-30

### 🎉 Initial Release

#### Features

**Core Functionality:**
- ✅ Progressive questionnaire flow (9 questions)
- ✅ Single-choice and multiple-choice questions
- ✅ Real-time Jaccard similarity scoring
- ✅ Top 10 personalized recommendations
- ✅ Modern gradient UI design
- ✅ MongoDB integration

**Architecture:**
- ✅ Modular scoring algorithm
- ✅ Database client with caching
- ✅ Session state management
- ✅ Configuration management

**Documentation:**
- ✅ Comprehensive README
- ✅ Setup guide
- ✅ Usage guide
- ✅ Quick start guide
- ✅ Implementation summary

**Developer Tools:**
- ✅ Setup script for question tags
- ✅ Test/verification script
- ✅ Requirements file

**Files Created:**
- `app.py` - Main Streamlit application (396 lines)
- `modules/scoring.py` - Jaccard similarity algorithm
- `modules/db_client.py` - MongoDB operations
- `utils/config.py` - Configuration
- `setup_question_tags.py` - Setup tool
- `test_setup.py` - Verification tool
- Documentation files (README, SETUP, USAGE, QUICKSTART, IMPLEMENTATION_SUMMARY)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2025-10-30 | Fixed checkbox state bug |
| 1.0.0 | 2025-10-30 | Initial release |

---

## Upgrade Guide

### From v1.0.0 to v1.1.0

No action required! This is a bug fix that's fully backward compatible.

Simply pull the latest code and restart your Streamlit app:

```bash
cd recommendation-poc-app
git pull  # or update your files
streamlit run app.py
```

No database changes, no config changes, no breaking changes.

---

## Future Roadmap

### Planned Features
- [ ] Add "Back" button to navigate to previous questions
- [ ] Save user progress (persistent sessions)
- [ ] A/B test different scoring algorithms
- [ ] Add content filtering options
- [ ] Export recommendations feature
- [ ] User feedback mechanism
- [ ] Analytics dashboard

### Under Consideration
- [ ] User authentication
- [ ] Recommendation history
- [ ] Social sharing
- [ ] Mobile optimization
- [ ] Multi-language support

---

**Current Version:** 1.1.0  
**Status:** Production Ready  
**Last Updated:** October 30, 2025

