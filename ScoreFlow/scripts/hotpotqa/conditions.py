TASK_PROMPT = '''### Problem Domain Overview

This domain tests multi-hop reasoning capability by requiring information synthesis across multiple Wikipedia documents to answer complex questions.

#### Key Characteristics & Requirements
- **Validation**: Answer must be factually correct based on provided documents
- **Critical**: Must connect information across 2+ documents through reasoning chains
- **Answer Format**: Short text spans (entities/phrases) or yes/no responses
- **Evidence Chain**: Must identify supporting facts from different documents
- **Precision**: Extract exact answer spans from text, not paraphrased

#### Common Question Types & Solution Strategies
- **Bridge Questions**: Connect documents through shared entities (e.g., "What nationality is the director of [movie]?")
- **Comparison Questions**: Compare properties across documents (e.g., "Which was founded first, X or Y?")
- **Compositional Questions**: Combine multiple facts to derive answer
- **Key Strategy**: Identify "bridge entity" that connects documents, then follow reasoning chain

#### Workflow Focus Points
1. Identify question type (bridge vs comparison)
2. Find bridge entities connecting documents
3. Build explicit reasoning chain across documents
4. Extract precise answer from final document
5. Return short, factual answer directly

#### Input Format
```
---
**CONTEXT DOCUMENTS:**

Document 1: [Title]
[paragraph of sentences]

Document 2: [Title]
[paragraph of sentences]
...

**QUESTION:**
[question requiring multi-hop reasoning]
---
```
Multiple problems follow the same structure if provided.
```
'''