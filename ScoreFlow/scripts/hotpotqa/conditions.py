TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **HotPotQA benchmark** (Multi-hop Question Answering). These problems test multi-document reasoning and information synthesis across Wikipedia articles.

**Core Characteristics:**
- **Input:** Multiple context documents (Wikipedia article excerpts) paired with a question requiring multi-hop reasoning
- **Required Skills:** Cross-document inference, entity tracking, fact chaining, and logical reasoning
- **Answer Types:** Short text spans (entity names, phrases), yes/no answers, or brief factual responses

**Question Types:**
- **Bridge Questions:** Require connecting information from multiple documents through shared entities
- **Comparison Questions:** Compare properties of entities mentioned across different documents
- **Compositional Questions:** Combine multiple facts to derive the answer

**Common Question Patterns:**
- **Bridge Entity:** "Who wrote the screenplay for [movie that actor X was in]?"
- **Property Comparison:** "Which was founded first, [Company A] or [Company B]?"
- **Multi-hop Facts:** "What nationality is the director of [movie]?"
- **Date/Time Questions:** "When did [person who did X] die?"

**Critical Challenges:**
- **Document Selection:** Identifying which documents contain relevant information
- **Entity Resolution:** Matching entities across different documents (same entity, different mentions)
- **Reasoning Chain:** Building correct inference chains from Document A → Bridge Entity → Document B
- **Supporting Facts:** Identifying specific sentences that support the answer

**Key Success Factors:**
- Identifying the reasoning type (bridge vs. comparison)
- Finding the "bridge entity" that connects documents
- Tracking entity mentions across multiple contexts
- Building explicit reasoning chains before answering
- Extracting precise answer spans from the text

'''