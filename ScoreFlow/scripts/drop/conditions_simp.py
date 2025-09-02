"""
Simplified conditions for drop benchmark
System prompts removed and operator descriptions simplified
Based on research showing improved diversity with this approach
"""

TASK_PROMPT = '''
### 1. Problem Domain Overview
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
