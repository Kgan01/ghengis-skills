# Learning Paths -- Evaluation

## TC-1: Happy Path -- Design a Learning Path from Scratch
- **prompt:** "I want to learn machine learning. I know Python basics and some high school math. Design a learning path for me."
- **context:** Learner with partial prerequisites wants to reach a well-defined target skill. Tests prerequisite mapping and curriculum design.
- **assertions:**
  - Response assesses current knowledge (Python basics, high school math) against ML prerequisites
  - Missing prerequisites are identified (linear algebra, calculus, probability, advanced Python)
  - Learning path is topologically sorted -- prerequisites come before dependent topics
  - Curriculum follows Bloom's taxonomy progression (remember/understand -> apply -> analyze/evaluate -> create)
  - Phases are defined with estimated durations (weeks) and activities
  - A capstone/create-level project is included at the end
- **passing_grade:** 5/6 assertions must pass

## TC-2: Edge Case -- Learner Wants to Skip Prerequisites
- **prompt:** "I want to jump straight into deep learning. I don't want to waste time on math fundamentals."
- **context:** Learner wants to skip foundational prerequisites. Tests the "Skipping Prerequisites" pitfall handling.
- **assertions:**
  - Response does NOT simply comply and jump to deep learning
  - Explains why prerequisites matter (can't skip Bloom's levels -- must remember/understand before apply)
  - Identifies specific math prerequisites needed for deep learning (linear algebra, calculus, probability)
  - Offers a compromise: accelerated coverage of prerequisites rather than skipping them entirely
  - Provides rationale for each prerequisite (why it matters for deep learning specifically)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Quality Check -- Time Estimation and Pacing
- **prompt:** "I can study 5 hours per week. How long will it take me to learn web development from scratch?"
- **context:** Tests learning velocity estimation with constrained study time. Should produce realistic timeline.
- **assertions:**
  - Response uses the learning velocity estimation formula (base hours adjusted by experience and related knowledge)
  - Provides a total hour estimate and converts to weeks based on 5 hours/week
  - Breaks the timeline into phases with per-phase durations
  - Recommends a mix of passive and active learning (not all video watching)
  - Includes spaced repetition schedule for retention
  - Sets realistic expectations (not promising mastery in 2 weeks at 5 hrs/week)
- **passing_grade:** 4/6 assertions must pass

## TC-4: Edge Case -- Tutorial Hell Detection
- **prompt:** "I've been watching Python tutorials for 6 months but I still don't feel like I can build anything on my own."
- **context:** Learner is stuck in tutorial hell. Tests the skill's ability to diagnose and correct this pitfall.
- **assertions:**
  - Response identifies this as the "Tutorial Hell" pitfall
  - Recommends shifting to active learning -- building projects, not watching more tutorials
  - Suggests a specific ratio (70% active / 30% passive for intermediate learners)
  - Proposes concrete project ideas appropriate to the learner's level
  - Recommends moving up Bloom's taxonomy: from remember/understand to apply/create
- **passing_grade:** 4/5 assertions must pass

## TC-5: Happy Path -- Progress Tracking Setup
- **prompt:** "I'm 4 weeks into learning React. I finished the basics tutorial and built a todo app. How am I doing and what's next?"
- **context:** Learner wants a progress check and next steps. Tests the progress tracking methodology.
- **assertions:**
  - Response assesses current Bloom level (likely at Apply stage based on building a todo app)
  - Identifies what the learner has mastered vs what gaps remain
  - Provides a clear next step that moves up the taxonomy (analyze/evaluate -- e.g., code reviews, comparing patterns)
  - Estimates remaining time to reach a higher proficiency level
  - Recommends a review/retention activity for already-learned material (spaced repetition)
- **passing_grade:** 4/5 assertions must pass
