"""
Simplified conditions for high_level_math_ganluo benchmark
System prompts removed and operator descriptions simplified
Based on research showing improved diversity with this approach
"""

TASK_PROMPT = '''
### 1. Problem Domain Overview
The target domain is the **AIME benchmark** (American Invitational Mathematics Examination). These are competition-level mathematics problems requiring sophisticated problem-solving techniques and deep mathematical insight.

**Core Characteristics:**
- **Input:** A precisely-stated mathematical problem, often with multiple constraints and conditions
- **Required Skills:** Advanced algebraic manipulation, geometric reasoning, combinatorial analysis, number theory, and creative problem-solving

**Common Problem Categories:**
- **Combinatorics & Probability:** Counting arrangements, expected values, recursive structures
- **Number Theory:** Divisibility, modular arithmetic, prime factorization, Diophantine equations
- **Geometry:** Coordinate geometry, synthetic geometry, area/volume calculations, trigonometry
- **Algebra:** Polynomial equations, functional equations, sequences and series, inequalities
- **Cross-domain Problems:** Problems combining multiple mathematical areas

**Advanced Techniques Often Required:**
- **Casework Analysis:** Systematically considering different scenarios
- **Recursive Formulas:** Building solutions from simpler cases
- **Generating Functions:** For counting problems
- **Coordinate Bashing:** Converting geometry to algebra
- **Symmetry Exploitation:** Using problem symmetry to simplify
- **Modular Arithmetic:** For number theory problems
- **Probabilistic Methods:** Expected value calculations, linearity of expectation

**Critical Challenges:**
- **Multiple Solution Paths:** Problems often have several approaches (algebraic, geometric, combinatorial)
- **Hidden Structure:** Key insights may not be immediately apparent
- **Computational Complexity:** Even with the right approach, calculations can be intricate
- **Constraint Management:** Multiple conditions that must all be satisfied simultaneously
- **Edge Cases:** Special cases that need separate consideration

**Key Success Factors:**
- **Problem Decomposition:** Break complex problems into manageable sub-problems
- **Pattern Recognition:** Identify familiar structures or techniques from simpler problems
- **Systematic Exploration:** Try multiple approaches if the first doesn't work
- **Rigorous Verification:** Check answer satisfies all constraints and makes mathematical sense
- **Simplification Skills:** Transform complex expressions into manageable forms
- **Boundary Testing:** Consider extreme cases to guide intuition


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
