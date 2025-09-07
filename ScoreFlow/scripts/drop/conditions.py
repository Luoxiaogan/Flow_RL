TASK_PROMPT = '''### Problem Domain Overview

This domain tests reading comprehension requiring discrete operations over text. Problems involve extracting information from Wikipedia passages and performing operations like counting, addition, subtraction, or comparison to answer questions.

#### Key Characteristics & Requirements
- **Validation**: Answers must match expected format (numbers, dates, or text spans)
- **Multi-hop Reasoning**: Questions often require combining multiple pieces of information
- **Reference Resolution**: Must resolve pronouns and partial names to correct entities
- **Discrete Operations**: Addition, subtraction, counting, sorting, comparison
- **Exact Extraction**: Text span answers must match the passage exactly

#### Common Problem Types & Solution Strategies
- **Arithmetic**: "How many total..." (addition), "How many more..." (subtraction), "What is the difference..." (subtraction)
- **Counting**: "How many times...", "How many different...", "How many [entity] did..."
- **Comparison**: "Which is greater/longer...", "Who had more...", "Which came first/last..."
- **Span Extraction**: "Who did...", "What was the name of...", "When did..."
- **Multi-step**: Questions requiring chaining multiple operations or facts

#### Workflow Focus Points
1. Extract ALL relevant entities and numbers from the passage
2. Map question references to specific passage entities (resolve "they", "the team", etc.)
3. Identify the required operation(s) from question phrasing
4. Execute operations carefully (don't miss any instances)
5. Format answer appropriately (number only, date format, exact text span)

#### Input Format
```
---
**PASSAGE:**
[Dense factual passage, often about sports, history, or demographics]

**QUESTION:**
[Question requiring discrete reasoning over the passage]
---
```
Multiple problems follow the same structure if provided.
'''