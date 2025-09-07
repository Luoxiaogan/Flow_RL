"""
Source benchmark: gsm8k

Auto-generated conditions for gsm8k_reasoning benchmark
Using operator group: reasoning_heavy
Generated at: 2025-09-07 14:46:18
"""
from ScoreFlow.scripts.common.base_conditions import (
    BASE_SYSTEM_PROMPT,
    BASE_PYTHON_END,
    BASE_RESPONSE_FORMAT
)

# ========== Benchmark-specific task description ==========
TASK_PROMPT = '''### Problem Domain Overview

GSM8K (Grade School Math 8K) tests multi-step mathematical reasoning through word problems requiring 2-8 sequential calculations using basic arithmetic operations.

#### Key Characteristics & Requirements
- **Answer Format**: Single numerical value (integer or decimal)
- **Solution Steps**: 2-8 step reasoning chains using +, -, ×, ÷
- **Critical**: Track intermediate results and units throughout
- **Validation**: Final answer must be numerically exact
- **No Complex Math**: Only elementary arithmetic, no algebra or calculus

#### Common Problem Types & Solution Strategies
- **Sequential Operations**: Step-by-step calculations building on previous results
- **Rate Problems**: Distance/speed/time, work rates, unit prices
- **Distribution**: Dividing quantities, equal sharing, remainders
- **Proportions**: Percentages, fractions, ratios, scaling
- **Multi-entity**: Track different quantities for multiple people/objects

#### Workflow Focus Points
1. Extract all numerical values and their context
2. Identify what the question asks for
3. Build step-by-step calculation chain
4. Show intermediate results explicitly
5. Return final numerical answer only

#### Input Format
```
---
**QUESTION:**
[Complete word problem text]
---
```
Multiple problems follow the same structure if provided.'''

# ========== System prompt (using common template) ==========
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT

# ========== Python start section with imports ==========
PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

# ========== Python end section (using common template) ==========
PYTHON_END = BASE_PYTHON_END

# ========== Operator descriptions and instructions ==========
START_PROMPT = '''### 2. Available Operators & Building Blocks

**Using Operator Group: 推理增强组**
**Description: 适合复杂推理任务，包含问题分解和多步推理**

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.


**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as "**Original Problem:**" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.



#### **CRITICAL: Understanding Parameters**

**The `instruction` Parameter (Required for all operators):**
- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do
- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous
- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)
- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, detailed reasoning strategies, and formatted requirements
- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded in the workflow structure. While instructions can dynamically incorporate relevant extracted information to guide the operation, the main data to be processed should remain in the context parameter.

**The `context` Parameter (Required for all operators except Generate):**
- **Purpose:** Provides the INPUT DATA that the instruction will operate on
- **Content:** The actual text, data, or results from previous operations - this is the primary information source
- **Type:** String for Generate/Revise/Summarize operators
- **Usage:** Think of it as the "working material" that the instruction processes
- **Note:** Ensemble uses `contexts` (plural) which takes List[str] instead of a single string


### Core Operators

**1. Generate: 创建新的信息或分析**
- **Signature:** `await self.generate(instruction: str, context: str = '') -> str`
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions

**2. Decompose: 分解复杂问题**
- **Signature:** `await self.decompose(instruction: str, context: str) -> str`
- **Purpose:** Breaks down complex problems into smaller sub-problems

**3. Revise: 改进和优化现有内容**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria

**4. Summarize: 压缩和提取关键信息**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information relevant to the problem

**5. Ensemble: 整合多个候选方案**
- **Signature:** `await self.ensemble(instruction: str, contexts_list: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions

**6. FormatAnswer: 格式化最终答案**
- **Signature:** `await self.formatanswer(instruction: str, context: str) -> str`
- **Purpose:** Formats the final answer according to specified requirements


### 3. Key Design Principles

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
```

### 4. Your Task: Complete the `run_workflow` Method

Your task is to write the Python code for the `run_workflow` method within the provided template. Focus on creating a robust, reusable workflow that leverages detailed instructions.

**Base Template:**

<think>
First, I need to deeply understand the core characteristics of this problem class. The goal is to design a workflow that is robust and generic.

My strategy will be to [Your step-by-step reasoning for the general problem class goes here...].

I've chosen the `Generate` operator for the initial step because [Your design decision explanation...]. This approach is superior to [alternative approach] because [justification...].
</think>
```python
# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        # [OPERATOR INITIALIZATION WILL BE DYNAMICALLY GENERATED]

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio
        # --- YOUR WORKFLOW LOGIC HERE ---
```

### 5. Critical Rules

**A. Generality:** Create templates for problem CLASSES, not specific instances
**B. Instructions:** Use comprehensive, detailed instructions (100-500+ words OK)
**C. Parameters:** `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble
**D. Control Flow:** Branch on operator results, not direct problem_text parsing
**E. Complexity:** Typically 3-8 operator calls, parallelize when possible
**F. Response Format:** ONLY `<think>...</think>` followed by ` ```python ... ``` `
'''

# ========== Operator initialization code for reference ==========
# This shows how operators should be initialized in the __init__ method
OPERATOR_INIT_CODE = '''
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.formatanswer = operator.FormatAnswer(self.llm, self.problem_text)'''

# ========== Configuration metadata ==========
OPERATOR_GROUP = "reasoning_heavy"
BENCHMARK_NAME = "gsm8k_reasoning"
