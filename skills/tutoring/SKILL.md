---
name: tutoring
description: Use when teaching or explaining concepts at any level — covers Socratic method, level assessment, worked examples, misconception handling, and adaptive difficulty
---

# Tutoring

## When to Use
When teaching concepts, explaining topics, answering learning questions, creating exercises, or adapting explanations to a learner's level. Use the Socratic method -- guide discovery, don't just dump information.

## Core Instructions

1. **Assess the learner's level first** -- ask what they already know, or infer from their question
2. **Start with the "why"** -- why does this matter? What problem does it solve?
3. **Use analogies** -- connect new concepts to things they already understand
4. **Build incrementally** -- don't jump to complex details before foundations are solid
5. **Give one concept at a time** -- don't overload. Teach A, confirm understanding, then teach B
6. **Use examples before definitions** -- show it working, then explain the theory
7. **Check understanding** -- ask "Does that make sense?" or pose a quick question
8. **Encourage mistakes** -- errors are learning opportunities, not failures

## Teaching Response Structure

When tutoring, aim to include these elements:
- **Level assessment**: beginner, intermediate, or advanced
- **Explanation**: The main teaching content (uses analogies, examples)
- **Concrete example**: A worked example showing the concept in action
- **Check understanding**: A question to verify they got it
- **Next step**: What to learn next if they understood this
- **Common misconception**: A mistake learners often make here

## Worked Examples

### Example 1 -- Beginner: "What is an API?"

**Level**: Beginner (non-technical).
**Approach**: No technical background. Use a real-world analogy. Avoid jargon entirely.

**Explanation**: Think of a restaurant. You (the customer) want food from the kitchen, but you can't just walk in and cook. Instead, you use a waiter -- you tell the waiter what you want, the waiter goes to the kitchen, and brings back your food.

An API is like that waiter. It's a messenger that takes your request to a system, and brings back the response. When you check the weather on your phone, your app sends a request through an API to a weather service, and the API brings back today's forecast.

**Example**:
```
When you type a city into a weather app:
1. Your app sends a request: "What's the weather in NYC?"
2. The API carries that request to the weather service
3. The weather service looks up NYC weather
4. The API brings back: "Sunny, 72F"
5. Your app shows you the result
```

**Check understanding**: If you wanted to build an app that shows movie ratings, what would the API do in that situation?

**Next step**: Learn about REST APIs -- the most common type, like a standardized menu format that all restaurants agree to use.

**Common misconception**: People think APIs are complicated software. They're just a communication standard -- a way for two programs to talk to each other.

### Example 2 -- Intermediate: "Explain recursion"

**Level**: Intermediate (knows programming basics).
**Approach**: They know functions and variables but recursion is abstract. Use a visual, step-by-step trace.

**Explanation**: Recursion is when a function calls itself to solve a smaller version of the same problem.

Imagine you're in a line of people and someone asks "What row are you in?" You don't know, so you ask the person in front of you. They don't know either, so they ask the person in front of THEM. This continues until the first person says "I'm row 1." Then each person adds 1 and passes it back. That's recursion.

Every recursive function needs:
1. A **base case** -- when to stop (the first person in line)
2. A **recursive case** -- the smaller problem (asking the person ahead)

**Example**:
```python
def factorial(n):
    if n <= 1:       # Base case: stop here
        return 1
    return n * factorial(n - 1)  # Recursive case

# factorial(4) works like this:
# factorial(4) = 4 * factorial(3)
# factorial(3) = 3 * factorial(2)
# factorial(2) = 2 * factorial(1)
# factorial(1) = 1  (base case!)
# Now unwind: 2*1=2, 3*2=6, 4*6=24
```

**Check understanding**: Can you write a recursive function that counts down from N to 0, printing each number? What's the base case?

**Next step**: Try solving "reverse a string" recursively. Then learn about stack overflow -- what happens when you forget the base case.

**Common misconception**: People think recursion is always better than loops. It's not -- it uses more memory (each call adds to the stack). Use it when the problem is naturally recursive (trees, fractals, divide-and-conquer).

### Example 3 -- Advanced: "When should I use a B-tree vs LSM-tree?"

**Level**: Advanced.
**Approach**: Advanced learner, they know both exist. Go straight to trade-offs with specific use cases.

**Explanation**: It's a read-vs-write trade-off:

**B-tree**: Optimized for reads. Data is sorted on disk in pages. Reads are O(log n) page lookups. Writes require finding the right page and potentially splitting it -- slower for write-heavy workloads. Used by: PostgreSQL, MySQL InnoDB.

**LSM-tree**: Optimized for writes. Writes go to an in-memory buffer (memtable), then flush to sorted files (SSTables) on disk. Reads may need to check multiple levels -- slower for point lookups. Used by: RocksDB, Cassandra, LevelDB.

Rule of thumb: Read-heavy (OLTP, user-facing) -> B-tree. Write-heavy (logs, time-series, IoT) -> LSM-tree.

**Example**:
```
Concrete scenario:
- User profile database (80% reads, 20% writes) -> B-tree (PostgreSQL)
- IoT sensor data (5% reads, 95% writes) -> LSM-tree (RocksDB/TimescaleDB)
- Mixed workload -> Consider RocksDB with bloom filters to speed up reads
```

**Check understanding**: You're designing a chat app that stores messages (write-heavy) but also needs fast message search (read-heavy). Which would you choose, and how would you optimize the weak side?

**Next step**: Look into hybrid approaches: TiDB uses both. Also study write amplification in LSM-trees -- it's the hidden cost.

**Common misconception**: People assume LSM-trees are always faster for writes. At scale, compaction (merging SSTables) creates write amplification that can actually make sustained write throughput worse than B-trees.

## Edge Cases

- **Learner says "I know nothing"**: Start with the absolute basics. Use only everyday analogies.
- **Learner is frustrated**: Acknowledge the difficulty first ("This IS hard -- most people struggle here"), then simplify.
- **Wrong mental model**: Gently correct by showing where the model breaks down, not by saying "you're wrong."
- **Multiple questions at once**: Pick the most foundational one, answer it, then address the others in order.

## Quality Checklist

- [ ] Level assessment matches the explanation depth
- [ ] At least one analogy or real-world comparison used
- [ ] Concrete example included (not just abstract explanation)
- [ ] Check-understanding question is answerable from the explanation
- [ ] Next step is provided for continued learning
- [ ] Common misconception is addressed
- [ ] Tone is encouraging, not condescending
