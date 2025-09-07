"""
Simplified conditions for gsm8k benchmark
System prompts removed and operator descriptions simplified
Based on research showing improved diversity with this approach
"""

TASK_PROMPT = '''
### 1. Problem Domain Overview
The target domain is the **GSM8K benchmark** (Grade School Math 8K). These are mathematical word problems designed at elementary school difficulty level.

**Core Characteristics:**
- **Input:** A word problem describing a real-world scenario with embedded numerical values and relationships
- **Required Skills:** Mathematical modeling, sequential calculation, unit tracking, and arithmetic operations
- **Answer Type:** Always a single numerical value (integer or decimal)

**Common Problem Types:**
- **Sequential Operations:** Multiple steps that build on each other (deposit then withdrawal)
- **Rate Problems:** Distance/speed/time, work rates, unit prices
- **Proportional Reasoning:** Ratios, percentages, fractions, scaling
- **Distribution Problems:** Dividing quantities, equal sharing, remainders
- **Comparison Problems:** Finding differences, determining "how many more"
- **Multi-entity Tracking:** Problems involving multiple people/objects with different quantities

**Mathematical Operations:**
- Basic arithmetic: addition, subtraction, multiplication, division
- Fractions and decimals
- Percentages and proportions
- Simple algebra (solving for unknowns)
- Unit conversions

**Critical Challenges:**
- **Hidden Steps:** Some calculations require intermediate steps not explicitly stated
- **Order of Operations:** Must correctly sequence multiple calculations
- **Unit Consistency:** Keeping track of units (dollars, hours, items) throughout
- **Contextual Constraints:** Real-world constraints (can't have negative items, fractional people)

**Key Success Factors:**
- Clear identification of known values and unknowns
- Systematic step-by-step calculation with explicit intermediate results
- Verification that the answer makes sense in context
- Proper handling of units and decimal places
- Working through the problem chronologically when time-based


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
