TASK_PROMPT = '''### Problem Domain Overview

SimpleQA (World Knowledge Question Answering) tests problem-solving capabilities in the specified domain.

#### Key Characteristics & Requirements
- **Input:** Factual questions requiring world knowledge
- **Output:** Concise, accurate answers (usually entities, dates, or short facts)
- **Skills:** Knowledge retrieval, fact verification, reasoning about real-world information
- **Topics:** Science, technology, geography, history, culture, and more

#### Input Format
```
---
**PROBLEM:**
[Complete problem statement]
---
```
Multiple problems follow the same structure if provided.'''


OPERATOR_PROMPT_PART_1 = '''### Available Operators

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.

**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as "**Original Problem:**" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.

**1. Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions

**2. Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria

**3. Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information relevant to the problem

**4. Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions'''

SYSTEM_PROMPT = '''You are an expert System Architect specializing in designing universal workflow solutions. Your task is to create a generalizable Python workflow that can solve ALL problems within a specific domain, not just individual examples.

You will receive:
1. Domain overview and problem characteristics
2. 1-3 concrete problem examples from this domain
3. Available operators (your only building blocks)
4. Output requirements

Your goal: Design a robust workflow that handles the entire problem class by identifying common patterns and creating a reusable solution strategy.

**Response Format:**
1. Provide your reasoning in a `<think>...</think>` block
2. Include a ```python``` code block with the complete workflow implementation

The workflow must be generic enough to handle ANY problem instance from the described domain, not just the provided examples.'''

OPERATOR_PROMPT_PART_2 = '''#### **CRITICAL: Understanding Operator Parameters**

**The `instruction` Parameter (Required for all operators):**
- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do
- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous
- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)
- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, detailed reasoning strategies, and formatted requirements
- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded in the workflow structure. While instructions can dynamically incorporate relevant extracted information to guide the operation, the main data to be processed should remain in the context parameter.

**The `context` Parameter (Required for all operators except `Ensemble`, which uses `contexts` instead of `context`):**
- **Purpose:** Provides the INPUT DATA that the instruction will operate on
- **Content:** The actual text, data, or results from previous operations - this is the primary information source
- **Type:** String for Generate/Revise/Summarize operators
- **Usage:** Think of it as the "working material" that the instruction processes
- **Note:** Ensemble uses `contexts` which takes List[str] instead of a single string

### Key Design Principles

**Dynamic Instruction Construction:**
Extract information early, then incorporate it into subsequent instructions using f-strings:
```python
extraction = await self.generate(instruction="Extract all numerical values...", context=self.problem_text)
analysis = await self.generate(
    instruction=f"Given these extracted values: {extraction}\nNow solve step by step...",
    context=self.problem_text
)
```

**Parallel Execution:**
Use `asyncio.gather()` for independent operations:
```python
results = await asyncio.gather(
    self.generate(instruction="Approach 1...", context=...),
    self.generate(instruction="Approach 2...", context=...)
)
final = await self.ensemble(instruction="Select best...", contexts=results)
```

**Common Pitfalls:**
- Don't hardcode problem-specific data in workflow code
- Don't use `await` inside list comprehensions (blocks parallelism)
- Do use detailed instructions (100-500+ words when needed)
- Do extract info dynamically and incorporate into instructions

#### **Innovation Guidelines:**

**Maximize the power of instructions by:**
- Building multi-paragraph instructions that leave nothing to interpretation
- Dynamically incorporating ALL relevant extracted information
- Creating instruction templates that adapt based on detected patterns
- Using instructions to implement complex reasoning strategies
- Including specific formatting requirements and output structures

**Remember:**
- Instructions are mini-prompts - make them as detailed as needed
- Extract early, enrich instructions throughout
- The workflow provides structure; instructions provide intelligence
- Never hardcode problem-specific data in the workflow code itself
- Always pass context appropriately - empty string for initial Generate, List for Ensemble

#### **Common Pitfalls to Avoid:**

```python
# WRONG: Hardcoding problem-specific information
result = await self.generate(
    instruction="Count how many field goals the Patriots scored",  # Too specific!
    context=self.problem_text
)

# CORRECT: Generic instruction that works for any problem
result = await self.generate(
    instruction="Identify what the question is asking for, then count or calculate the requested value",
    context=self.problem_text
)

# WRONG: Sequential execution when parallel is possible
result1 = await self.generate(...)  # Waits
result2 = await self.generate(...)  # Then waits again

# CORRECT: Parallel execution for independent operations
results = await asyncio.gather(
    self.generate(...),
    self.generate(...)
)
```'''


USER_PROMPT_LONG ='''### Your Task: Complete the `run_workflow` Method

Your task is to write the Python code for the `run_workflow` method within the provided template below. Focus on creating a robust, reusable workflow that leverages detailed instructions.

**Response Format:**
1. Provide your reasoning in a `<think>...</think>` block
2. Include a ```python``` code block with the complete workflow implementation

**Base Template:**
<think>
Design a universal workflow for this problem domain. Consider:
- Core patterns and variations across the domain
- Multiple solution strategies and their trade-offs
- For each operator in your workflow: why it's necessary, how to craft its instructions, and how it connects with other operators
- How your design ensures the workflow solves ANY problem in this domain (not just the examples shown)

Write detailed reasoning (aim for 8-10 paragraphs) explaining your workflow design decisions.
</think>
Feel free to add any additional explanations before or after the code.
```python
# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        import asyncio
        # --- YOUR WORKFLOW LOGIC HERE ---
```
Feel free to add any additional explanations before or after the code.

**Critical Rules:**

1. Generality: The workflow must be generic enough to handle ANY problem instance from the described domain, not just the provided examples.
2. Instructions: Use comprehensive, detailed instructions (100-500+ words OK)
3. Parameters: `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble
4. Control Flow: Branch on operator results, not direct problem_text parsing
5. Complexity: Typically 3-8 operator calls, parallelize when possible'''


PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''
    async def __call__(self):
        """
        Main entry point that executes the workflow.
        """
        TIMEOUT = {time}

        try:
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return raw_result

        except asyncio.TimeoutError:
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            import traceback
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred. Details: {{escaped_error_details}}"
'''
