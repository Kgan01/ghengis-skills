---
name: learning-paths
description: Use when helping someone learn a new subject or skill — covers Bloom's taxonomy, prerequisite mapping, curriculum design, and personalized learning progression
---

# Learning Path Design

## When to Use
When helping someone learn a new subject or skill, designing a curriculum, identifying knowledge gaps, creating study plans, recommending learning resources, or structuring educational progression from beginner to mastery.

## Core Concepts

### Bloom's Taxonomy (Learning Levels)

Six levels of cognitive complexity (bottom to top):

```
1. REMEMBER (recall facts)
   - Keywords: define, list, name, identify, recall
   - Activities: flashcards, quizzes, memorization
   - Assessment: "What is X?", "List the steps"
   - Example: "Define photosynthesis"

2. UNDERSTAND (explain concepts)
   - Keywords: explain, describe, summarize, compare
   - Activities: explanations, concept maps, paraphrasing
   - Assessment: "Explain why X happens"
   - Example: "Describe how photosynthesis works"

3. APPLY (use in new situations)
   - Keywords: solve, calculate, demonstrate, use
   - Activities: problem sets, simulations, role-play
   - Assessment: "Solve this problem using X"
   - Example: "Calculate energy output of a plant"

4. ANALYZE (break down, find patterns)
   - Keywords: compare, contrast, examine, differentiate
   - Activities: case studies, diagrams, critiques
   - Assessment: "What are the differences between X and Y?"
   - Example: "Compare C3 vs C4 photosynthesis"

5. EVALUATE (make judgments)
   - Keywords: judge, critique, defend, justify
   - Activities: debates, reviews, recommendations
   - Assessment: "Which approach is better and why?"
   - Example: "Evaluate strategies to maximize plant growth"

6. CREATE (produce something new)
   - Keywords: design, construct, develop, formulate
   - Activities: projects, experiments, presentations
   - Assessment: "Design a system that..."
   - Example: "Design an optimal greenhouse environment"

Key principle: Can't skip levels. Must Remember->Understand before Apply.
```

### Prerequisite Mapping

When designing a learning path, build a dependency graph of topics.

**Example dependency chains:**
```
calculus requires: algebra, trigonometry, functions
machine_learning requires: linear_algebra, calculus, probability, python
web_development requires: html, css, javascript
react requires: web_development, javascript_es6, npm
typescript requires: javascript
backend_api requires: http_basics, database_basics, one_programming_language
```

**Process:**
1. Identify the target skill
2. List all prerequisites (recursively)
3. Assess what the learner already knows
4. Build a topologically sorted path from current knowledge to target
5. Estimate time for each gap

**Example:**
```
Current knowledge: python_basics, html, css
Target: machine_learning
Path: linear_algebra -> calculus -> probability -> python_advanced -> machine_learning
```

### Spaced Repetition

Optimize long-term retention by reviewing at increasing intervals.

**Review schedule:**
```
Day 1: Learn new concept
Day 2: First review (interval: 1 day)
Day 5: Second review (interval: 3 days)
Day 12: Third review (interval: 7 days)
Day 26: Fourth review (interval: 14 days)
Day 56: Fifth review (interval: 30 days)
...intervals continue to grow if recall is good
```

**Recall quality determines next interval:**
- Perfect recall -> increase interval
- Partial recall -> keep same interval
- Failed recall -> reset to beginning

### Learning Velocity Estimation

Estimate time to mastery based on:
- **Topic complexity**: Base hours for an average learner
- **Learner experience**: Beginner (1.5x longer), intermediate (1x), advanced (0.7x)
- **Related knowledge**: Each related topic known reduces time by ~10%
- **Study intensity**: Hours per week available

**Example:**
```
Target: Machine Learning (base: 80 hours)
Experience: Intermediate (1.0x)
Related topics known: Python, statistics (2 topics x 10% = 20% reduction -> 0.8x)
Adjusted: 80 x 1.0 x 0.8 = 64 hours
At 10 hours/week: ~6.4 weeks
```

## Patterns & Procedures

### Curriculum Design Process

When designing a learning curriculum, structure it in 4 phases aligned with Bloom's taxonomy:

**Phase 1: Foundation (Remember + Understand)**
- Duration: ~2 weeks
- Activities: video lectures, reading, concept quizzes, summary writing
- Assessment: concept quiz (pass threshold: 70%, mastery: 85%)

**Phase 2: Application (Apply)**
- Duration: ~3 weeks
- Activities: practice problems, code exercises, mini projects
- Assessment: practical exam (pass threshold: 75%)

**Phase 3: Integration (Analyze + Evaluate)**
- Duration: ~2 weeks
- Activities: case studies, comparative analysis, code reviews
- Assessment: analysis report (rubric: depth, accuracy, critical thinking)

**Phase 4: Mastery Project (Create)**
- Duration: ~3 weeks
- Activities: capstone project building a real-world application
- Assessment: project evaluation (functionality, quality, documentation, presentation)

### Knowledge Gap Identification

When a learner wants to reach a target skill:

1. **Check prerequisites**: List everything required for the target skill
2. **Assess current knowledge**: What does the learner already know?
3. **Find missing prerequisites**: Topics not yet learned
4. **Find weak foundations**: Topics known but below 70% proficiency
5. **Prioritize**: Strengthen weak foundations first, then learn new material
6. **Provide rationale**: Explain why each prerequisite matters for the target

### Progress Tracking

Track learner progress across multiple dimensions:
- **Overall completion**: Percentage of activities done
- **Bloom level mastery**: Score at each cognitive level
- **Time metrics**: Weeks elapsed, estimated remaining, on-track/behind/ahead
- **Retention score**: Performance on spaced repetition reviews
- **Recommendations**: Actionable suggestions based on data

### Learning Path Template

```json
{
  "title": "Python for Data Science",
  "target_audience": "Beginners with basic programming",
  "duration_weeks": 12,
  "hours_per_week": 10,
  "prerequisites": ["basic_programming", "high_school_math"],
  "phases": [
    {
      "name": "Python Fundamentals",
      "weeks": 3,
      "bloom_levels": ["remember", "understand", "apply"],
      "topics": ["variables", "functions", "loops", "data_structures"],
      "activities": ["video_lectures", "coding_exercises", "mini_projects"],
      "assessment": "coding_exam"
    },
    {
      "name": "Data Manipulation",
      "weeks": 3,
      "bloom_levels": ["apply", "analyze"],
      "topics": ["pandas", "numpy", "data_cleaning"],
      "activities": ["real_datasets", "analysis_projects"],
      "assessment": "data_analysis_project"
    },
    {
      "name": "Visualization & ML Basics",
      "weeks": 4,
      "bloom_levels": ["apply", "analyze", "evaluate"],
      "topics": ["matplotlib", "seaborn", "sklearn"],
      "activities": ["visualization_challenges", "ml_experiments"],
      "assessment": "ml_project"
    },
    {
      "name": "Capstone",
      "weeks": 2,
      "bloom_levels": ["create"],
      "topics": ["end_to_end_project"],
      "activities": ["build_portfolio_project"],
      "assessment": "presentation"
    }
  ]
}
```

## Common Pitfalls

### Skipping Prerequisites
- **Problem**: Learner jumps to advanced topic without foundation
- **Fix**: Enforce prerequisite checks, gate content until basics mastered

### Tutorial Hell
- **Problem**: Completing tutorials without building anything original
- **Fix**: Require capstone projects, real-world applications at each phase

### Passive Learning
- **Problem**: Watching videos, reading docs, but not practicing
- **Fix**: 70% active (coding, writing, problem-solving) vs 30% passive (reading, watching)

### No Spaced Repetition
- **Problem**: Learn once, forget later, have to relearn
- **Fix**: Schedule reviews at increasing intervals (1 day, 3 days, 7 days, etc.)

### Not Tracking Progress
- **Problem**: Unclear how much left, losing motivation
- **Fix**: Visual progress bars, milestone celebrations, time estimates

### One Learning Style Only
- **Problem**: Only reading (or only watching videos)
- **Fix**: Mix modalities: read, watch, practice, teach, build

## Quick Reference

### Recommended Learning Time Blocks
```
Pomodoro technique (25min focus, 5min break):
- Best for: focus-intensive tasks (coding, problem-solving)
- Sessions per day: 4-8 (2-4 hours total)

Longer blocks (90min focus, 15min break):
- Best for: deep dives, reading, projects
- Sessions per day: 2-3

Active vs passive learning ratio:
- Beginners: 50% passive (learn), 50% active (practice)
- Intermediate: 30% passive, 70% active
- Advanced: 10% passive, 90% active (mostly building)
```

### Assessment Frequency
```
Formative (frequent, low stakes):
- Daily: Practice problems, flashcards
- Weekly: Quizzes, small projects
- Purpose: Identify gaps early

Summative (infrequent, high stakes):
- End of phase: Major exams, projects
- End of course: Capstone project
- Purpose: Certify mastery

Review schedule:
- Daily: 15min spaced repetition
- Weekly: 1hr review weak topics
- Monthly: 2hr comprehensive review
```

## Checklists

### Before Designing Learning Path
- [ ] Goal clearly defined (what learner wants to achieve)
- [ ] Current knowledge assessed (what learner already knows)
- [ ] Prerequisites identified (what's needed before starting)
- [ ] Time commitment realistic (hours per week available)
- [ ] Learning style preferences noted (visual, hands-on, reading)
- [ ] Success metrics defined (how to measure completion)

### During Curriculum Design
- [ ] Bloom's taxonomy progression (remember->create)
- [ ] Prerequisites taught before dependent topics
- [ ] Mix of passive (reading/watching) and active (building/practicing)
- [ ] Assessments align with Bloom levels (quiz for remember, project for create)
- [ ] Spaced repetition built in (reviews scheduled)
- [ ] Milestones defined (celebrate progress)

### Progress Monitoring
- [ ] Weekly check-in on completion rate
- [ ] Bloom level mastery scores tracked
- [ ] Retention/review performance monitored
- [ ] Struggling topics identified and remediated
- [ ] Pace adjusted if falling behind or racing ahead
- [ ] Motivation maintained with variety and wins
