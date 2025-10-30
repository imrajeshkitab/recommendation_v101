## Objective
Extract tags from book summaries that map directly to user onboarding responses for personalized recommendations.

## Instructions
Analyze the book summary and extract relevant tags across 8 categories. Each category maps to a specific onboarding question.

---

### **1. LIFE_STAGE_AGE** (Maps to: Age Group)
Does this content specifically address challenges, perspectives, or life phases relevant to:
- **16-25 years**: Early adulthood, finding identity, starting career
- **26-35 years**: Building career, relationships, establishing life
- **36-50 years**: Mid-life, established career, deeper questions
- **50+ years**: Wisdom, legacy, life reflection, transitions

**Extract tags:** ["young adult", "early twenties", "Gen Z", "college age", "career starter", "emerging adult", "millennials", "young professional", "career building", "settling down", "early thirties", "family planning", "mid-career", "Gen X", "established professional", "family focused", "midlife", "experienced", "mature", "senior", "experienced", "wisdom seeker", "retirement planning", "legacy building"]

---

### **2. LIFE_STAGE_RELATIONSHIP** (Maps to: Relationship Status)
Does this content address:
- **Single life**: Independence, self-focus, dating
- **In a relationship**: Dating dynamics, commitment, partnership
- **Married**: Marriage, long-term partnership, spouse dynamics
- **Divorced/Widowed**: Loss, new beginnings, recovery, reinvention

**Extract tags:** ["independent", "solo", "dating", "unattached", "available", "self-focused", "partnered", "dating", "committed", "couple", "romantic bond", "spouse", "committed partnership", "marital", "life partner", "family unit", "separated", "loss", "grief", "new beginning", "single again", "life transition"]

---

### **3. LIFE_STAGE_PARENTING** (Maps to: Do you have kids?)
Does this content specifically address:
- Parenting challenges, strategies, or perspectives
- Work-family balance
- Child development, education
- Parent-child relationships

**Extract tags:** ["parent", "caregiver", "family", "children", "parenting journey", "responsible", "childless", "child-free", "independent", "personal freedom", "solo lifestyle"]

**Note:** Only tag if content EXPLICITLY addresses parenting. Absence of tags = suitable for non-parents.

---

### **4. PRIMARY_NEED** (Maps to: What's on your mind?)
What is the PRIMARY transformation or outcome this book delivers?

Match to these user needs:
1. **Calm & Balance** → emotional regulation, stress relief, tranquility
2. **Confidence** → self-esteem, assertiveness, self-belief
3. **Relationships** → connection, communication, interpersonal skills
4. **Clarity** → direction, purpose, career guidance, life decisions
5. **Personal Growth** → self-improvement, potential, transformation
6. **Learning** → knowledge, curiosity, intellectual growth
7. **Exploration** → discovery, open-ended wisdom, browsing

**Extract tags:** ["peace", "balance", "stress relief", "mental health", "tranquility", "mindfulness", "emotional stability", "self-esteem", "confidence building", "self-assurance", "empowerment", "self-belief", "courage", "connection", "communication", "intimacy", "relationship skills", "empathy", "social bonds", "direction", "purpose", "career guidance", "life path", "decision making", "clarity seeking", "personal growth", "self-improvement", "development", "potential", "excellence", "transformation", "curiosity", "knowledge seeker", "lifelong learning", "intellectual growth", "exploration", "education", "casual", "browsing", "open-minded", "discovery", "experimental", "curious"]

---

### **5. MOTIVATION_DRIVER** (Maps to: What motivates you?)
What DEEPER emotional need or motivation does this fulfill?

1. **Peaceful inside** → serenity, emotional regulation, mindfulness
2. **Goals with less stress** → stress management, achievement, efficiency
3. **Discovering who I am** → identity, authenticity, self-discovery
4. **Better relationships** → empathy, emotional intelligence, nurturing
5. **Direction & purpose** → meaning, calling, life direction
6. **Better decisions** → wisdom, judgment, discernment

**Extract tags:** ["inner peace", "serenity", "calm", "mindfulness", "meditation", "stress-free", "harmony", "productivity", "efficiency", "work-life balance", "goal achievement", "stress management", "success", "self-discovery", "identity", "authenticity", "introspection", "self-awareness", "purpose", "relationships", "caregiving", "empathy", "connection", "love", "support", "interpersonal skills", "meaning", "life purpose", "direction", "vision", "mission", "clarity", "path finding", "decision making", "wisdom", "judgment", "priorities", "values", "intentional living"]

---

### **6. COGNITIVE_STYLE** (Maps to: How would you relate?)
What type of thinking or approach does this book appeal to?

1. **Logic & Analysis** → systematic thinking, planning, strategy
2. **Values & Emotion** → ethics, empathy, heart-centered
3. **Details & Facts** → practical, realistic, data-driven
4. **Ideas & Possibilities** → innovative, conceptual, future-thinking

**Extract tags:** ["analytical", "rational", "logical thinker", "planner", "strategic", "systematic", "thinking type", "empathetic", "values-driven", "emotional", "ethical", "compassionate", "feeling type", "moral", "practical", "detail-oriented", "realistic", "concrete", "sensory", "present-focused", "sensing type", "intuitive", "visionary", "creative", "innovative", "imaginative", "future-focused", "intuitive type"]

---

### **7. CONTENT_DEPTH** (Maps to: Time commitment)
How much depth and time investment does this content require?

- **5 min** → Quick insights, daily reflections, bite-sized wisdom
- **10 min** → Story-driven, narrative, engaging examples
- **15+ min** → Comprehensive exploration, deep analysis, thorough

**Extract tags:** ["busy", "time-constrained", "quick learner", "efficient", "brief sessions", "micro-learning", "moderate commitment", "balanced", "daily habit", "consistent", "story lover", "regular practice", "dedicated", "deep learner", "committed", "intensive", "thorough", "wisdom seeker", "patient"]

---

### **8. LEARNING_STYLE** (Maps to: Learning preference)
How is the content structured and delivered?

1. **Step by step** → Structured, methodical, gradual progression
2. **Exciting & powerful** → Inspiring, motivational, energizing
3. **Deep thinking** → Reflective, philosophical, contemplative
4. **What works** → Actionable, practical tips, results-focused

**Extract tags:** ["methodical", "patient", "gradual progress", "systematic learner", "steady growth", "incremental", "energetic", "impact-driven", "dynamic", "transformational", "bold", "high-intensity", "reflective", "philosophical", "contemplative", "analytical", "introspective", "thoughtful", "practical", "results-oriented", "pragmatic", "action-focused", "efficient", "no-nonsense"]

---