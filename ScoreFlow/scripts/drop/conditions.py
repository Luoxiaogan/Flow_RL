TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **DROP benchmark** (Discrete Reasoning Over Paragraphs). These problems test reading comprehension with discrete reasoning over text passages.

**Core Characteristics:**
- **Input:** A dense factual passage (often about sports, history, or demographics) paired with a question
- **Required Skills:** Information extraction, numerical reasoning, entity tracking, and multi-hop inference
- **Answer Types:** Numbers (counts, calculations), dates, text spans (entity names, phrases), or comparative answers

**Common Question Patterns:**
- **Arithmetic Operations:** "How many total/combined..." (addition), "How many more..." (subtraction), "What is the difference..." (subtraction)
- **Counting:** "How many times...", "How many different..."
- **Comparison:** "Which is greater/longer/more...", "Who had more..."
- **Selection:** "Which team won...", "What happened first/last..."
- **Span Extraction:** "Who did...", "What was the name of..."

**Critical Challenges:**
- **Ambiguous References:** Questions may use pronouns or partial names requiring coreference resolution
- **Multiple Similar Entities:** Passages often contain multiple similar items (e.g., multiple field goals of different yards)
- **Implicit Information:** Some answers require inference from context rather than direct extraction
- **Numerical Complexity:** May involve multiple numbers that need to be correctly associated with their entities

**Key Success Factors:**
- Exhaustive extraction of ALL relevant occurrences (don't miss any instance)
- Careful entity-number association (which number belongs to which entity)
- Understanding question intent (sum vs. individual value, all occurrences vs. specific one)
- Handling both explicit and implicit information

'''