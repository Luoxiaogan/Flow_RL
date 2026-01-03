"""
Simplified conditions for hotpotqa benchmark
System prompts removed and operator descriptions simplified
Based on research showing improved diversity with this approach
"""

TASK_PROMPT = '''
### 1. Problem Domain Overview
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

# SYSTEM_PROMPT removed - research shows training without system prompts
# but using them at inference improves both safety and diversity
SYSTEM_PROMPT = ''

PYTHON_START = '''
import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create


'''

PYTHON_END = '''


    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It returns the raw result from the workflow execution.
        """
        TIMEOUT = {time}

        try:
            # Execute the LLM-generated workflow to get the raw result.
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            
            # Return the raw result directly - answer extraction is now handled in handler
            return raw_result

        except asyncio.TimeoutError:
            # Handle workflow execution timeout gracefully.
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            # Handle other potential errors during workflow execution.
            import traceback
            # 错误详情在这里被定义和使用，不暴露给外部.format()
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred during workflow execution. Details: {{escaped_error_details}}"

'''

# Simplified START_PROMPT - reduced from ~3000 words to ~300 words
# Preserves all functional information while removing redundancy
START_PROMPT = '''
### 2. Core Operators

You have access to four fundamental operators, each pre-initialized with problem_text:
- **Generate(instruction: str, context: str = "") -> str**: Creates new content based on instructions
- **Revise(instruction: str, context: str) -> str**: Improves existing content
- **Summarize(instruction: str, context: str) -> str**: Condenses while preserving key information
- **Ensemble(instruction: str, contexts: List[str]) -> str**: Synthesizes multiple inputs

### 3. Meta-Learning Task & Implementation Guidelines

**Your Task:** Design a reusable Python workflow template that solves the entire problem CLASS, not specific instances. This is meta-learning - you're creating a system that learns patterns, not memorizing solutions.

**Key Guidelines:**
- Instructions should be comprehensive (100-500+ words when needed)
- Use f-strings for dynamic instruction construction
- Leverage asyncio.gather() for parallel operations
- Context parameter carries the actual data to process
- Never hardcode problem-specific information

**Response Format Required:**
1. A `<think>...</think>` block explaining your general solution strategy
2. A Python code block with the complete workflow implementation

**Template Structure:**
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # Pre-initialized operators - DO NOT MODIFY
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
    
    async def run_workflow(self):
        import asyncio
        # YOUR GENERIC WORKFLOW LOGIC HERE
        # Must work for ANY instance of this problem type
        pass
```
'''
