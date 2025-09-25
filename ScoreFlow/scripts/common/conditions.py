SYSTEM_PROMPT_RL_RIGHT = '''Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1. A high-level description of the problem domain
2. A strictly defined set of callable software "Operators" that serve as your only building blocks
3. An illustrative example instance, provided solely to help you understand the abstract reasoning pattern

**Your response MUST strictly adhere to the following two-part format:**

**1. A `<think>...</think>` block:**
Inside this block, you must articulate your complete reasoning process for creating a **general solution for the entire problem class**, not just the provided example. Your reasoning should include:
- A step-by-step analysis of the problem category.
- Consideration of different potential strategies and approaches.
- A clear explanation of your final design decisions and why you chose specific operators for the workflow.

**2. A Python Code Block:**
Immediately following the closing `</think>` tag, provide the complete and reusable Python solution. This code must be enclosed in markdown fences, specifically ` ```python ... ``` `.

---

### Example Response Structure:

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
        
{operators_init}

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
---

Your generated Python workflow must be robust enough to work for any problem instance within the described domain.'''

USER_PROMPT_PART_1_RL_RIGHT = '''### 2. Available Operators & Building Blocks

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

#### **Core Operators**
 
'''

generate = '''**Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions
'''

revise = '''**Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria
'''

summarize = '''**Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information relevant to the problem
'''

ensemble = '''**Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions
'''

programmer = '''**Programmer: EXECUTE code solutions**
- **Signature:** `await self.programmer(instruction: str, context: str = "") -> str`
- **Purpose:** Generates and executes Python code to solve computational problems
- **When to use:** Mathematical calculations, algorithmic problems, data processing, or any task requiring precise computation
- **Parameters:**
  - `instruction`: Programming task specification
  - `context`: Previous analysis or extracted data to inform code generation
  - `max_retries`: Number of attempts if code fails (default: 3)
- **Returns:** Execution results including generated code and output
- **Safety:** Automatically validates code safety and blocks dangerous operations
- **Example usage:** Solving math problems, implementing algorithms, data analysis, pattern matching
'''

decompose = '''**Decompose: BREAK DOWN complexity**
- **Signature:** `await self.decompose(instruction: str, context: str = "") -> List[Dict[str, str]]`
- **Purpose:** Systematically breaks complex problems into manageable subproblems with dependencies
- **When to use:** Handling multi-step problems, creating solution roadmaps, or identifying prerequisite tasks
- **Parameters:**
  - `instruction`: Decomposition strategy and granularity level
  - `context`: Additional information to guide decomposition
- **Returns:** List of dictionaries, each containing:
  - `id`: Unique identifier for the subproblem
  - `description`: Clear description of what needs to be solved
  - `dependencies`: Comma-separated IDs of prerequisite subproblems
- **Example usage:** Multi-step math problems, complex reasoning chains, hierarchical task planning
- **Important special note:** Decompose is special: it's output is a structured list of subproblems, which is List[Dict[str, str]]
'''

selfconsistency = '''**SelfConsistency: generating multiple independent solutions in parallel, then selecting the best one based on consistency and quality analysis.**

#### Overview

The `SelfConsistency` operator enhances solution reliability by generating multiple independent solutions in parallel, then selecting the best one based on consistency and quality analysis. This implements the self-consistency prompting technique, significantly improving accuracy over single-attempt generation.

#### Usage

```python
result = await self_consistency(
    instruction="Your specific instruction here",
    context="Previous context or information"
)
```

##### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `instruction` | `str` | `""` | Specific instruction for solving the problem |
| `context` | `str` | `""` | Context or information from previous workflow steps |

##### Return Value

Returns a string containing the complete best solution selected from multiple generated samples.

#### How It Works

1. **Parallel Generation**: Generates 5 independent solutions simultaneously using the `Generate` operator
2. **Intelligent Selection**: Analyzes all solutions using the `Ensemble` operator based on:
   - Answer consistency (majority voting)
   - Logical correctness
   - Reasoning quality
   - Solution completeness
3. **Output**: Returns the full text of the best solution

#### Example Use Cases

```python
# Mathematical problem solving
result = await self_consistency(
    instruction="Solve this equation step by step",
    context="Find all real solutions to x^3 - 2x - 5 = 0"
)

# Logical reasoning
result = await self_consistency(
    instruction="Analyze the argument and identify any logical fallacies",
    context="If it rains, the ground gets wet. The ground is wet. Therefore, it rained."
)

# Code generation
result = await self_consistency(
    instruction="Write an efficient Python function with proper error handling",
    context="Implement binary search for a sorted array"
)
```

#### Best Practices

1. **Clear Instructions**: Provide specific, unambiguous instructions for better consistency
2. **Complete Context**: Include all relevant information from previous steps
3. **Problem Types**: Works best for problems with deterministic answers (math, logic, coding)

#### Key Benefits

- **Higher Accuracy**: Reduces errors through consistency checking
- **Robustness**: Handles LLM variability effectively  
- **No Additional Latency**: Parallel execution maintains single-generation speed
- **Quality Selection**: Returns the best reasoned solution, not just the most common answer

#### Notes

- Diversity comes from natural LLM variability across multiple calls
- The operator respects the SCOREFLOW_SILENT environment variable
- Automatically handles partial failures (continues if some generations fail)
- Returns complete solution text, preserving all reasoning steps'''

verifyandrefine = '''**VerifyAndRefine: SELF-CORRECT and rigorously improve a solution**

-   **Signature:** `await self.verify_and_refine(instruction: str, context: str) -> str`
-   **Purpose:** Executes an automated, in-depth verification and refinement cycle to fix errors, fill logical gaps, and comprehensively enhance the quality and rigor of a solution. This is the most powerful tool for ensuring the final output is correct and robust.

---

### **Detailed Description**

#### **Key Features & Benefits**

1.  **Power & Simplicity:** This is a high-level operator that encapsulates a complex, multi-step self-correction process into a single, simple function call. It transforms a potentially flawed draft into a polished, correct solution in one line of code.
2.  **Automated Error Correction:** It goes beyond just *identifying* issues; it actively attempts to *fix* them. This includes:
    *   **Critical Errors:** Logical fallacies, calculation mistakes, incorrect application of formulas.
    *   **Justification Gaps:** Leaps in logic, missing proofs, hand-wavy explanations, or steps that lack sufficient reasoning.
3.  **Complexity Hidden:** You (the workflow-generating LLM) do **NOT** need to handle any complex internal data structures. There is no need to parse XML or JSON, check dictionary keys, or write `if/else` logic. The operator handles all verdict-checking and conditional logic internally.
4.  **Enhanced Rigor:** Beyond just fixing overt errors, this operator strives to elevate the overall quality of the solution, making it more logically sound, well-structured, and professionally articulated.

#### **How It Works Internally**

When you call this operator, it executes a rigorous internal process:

1.  **Verification:** An extremely meticulous 'internal verification expert' (`_internal_verifier`) examines the provided `context` (the solution draft) with the standards of an academic peer reviewer or a competition judge.
2.  **Decision:** The operator programmatically checks the `verdict` from the verification step. If the verdict is 'correct' and no issues are found, it immediately stops and returns the original solution, saving time and avoiding unnecessary changes.
3.  **Refinement:** If any issues are found, the verifier provides a detailed, structured report to an 'internal refinement expert' (`_internal_refiner`).
4.  **Return:** The 'refinement expert' uses this report to generate a new, improved version of the solution. This refined version is then returned. If the refinement process fails for any reason, the operator safely returns the original solution to prevent workflow interruption.

#### **Strategic Usage & Best Practices**

*   **When to Use It:**
    `VerifyAndRefine` should be used as the **final quality assurance gate** before producing the final answer. It is ideal after you have a complete solution draft from `generate` or `revise`. It acts as a powerful "self-correction" or "self-critique" step.

*   **How to Use the `instruction` Parameter:**
    This parameter sets a high-level goal for the refinement, influencing the *style* of the final corrected solution.
    *   Example 1: `instruction="Ensure the final solution is clear enough for a high-school student to understand."` (The corrected output will prioritize simplicity and clarity).
    *   Example 2: `instruction="Refine the proof to meet the publication standards of a mathematical journal."` (The corrected output will be more formal, dense, and rigorous).

*   **Difference from `Revise`:**
    *   `Revise` is a general-purpose "improvement" tool, often used for changes in style, tone, clarity, or format based on your instructions.
    *   `VerifyAndRefine` is a specialized "correction" tool focused on **correctness and logical rigor**. When you are unsure if a solution is *correct*, always prefer `VerifyAndRefine`.

#### **Canonical Example:**

This is the golden pattern you should follow in your workflows:

```python
# class Workflow:
#     async def run_workflow(self):

# Step 1: Generate an initial draft of the solution.
draft_solution = await self.generate(
    instruction="Solve the problem step-by-step, showing all calculations and reasoning.",
    context=self.problem_text
)

# Step 2: Use VerifyAndRefine as the final, powerful step to ensure correctness and quality.
final_solution = await self.verify_and_refine(
    instruction="Fix any and all errors. The final answer must be rigorously correct and well-explained.",
    context=draft_solution
)

# The 'final_solution' is now the highest quality version achievable through one self-correction loop.
return final_solution
```'''

generate_init = '''self.generate = operator.Generate(self.llm, self.problem_text)'''
revise_init = '''self.revise = operator.Revise(self.llm, self.problem_text)'''
summarize_init = '''self.summarize = operator.Summarize(self.llm, self.problem_text)'''
ensemble_init = '''self.ensemble = operator.Ensemble(self.llm, self.problem_text)'''
programmer_init = '''self.programmer = operator.Programmer(self.llm, self.problem_text)'''
decompose_init = '''self.decompose = operator.Decompose(self.llm, self.problem_text)'''
verifyandrefine_init = '''self.verify_and_refine = operator.VerifyAndRefine(self.llm, self.problem_text)'''
selfconsistency_init =  '''self.selfconsistency = operator.SelfConsistency(self.llm, self.problem_text)'''


USER_PROMPT_PART_2_RL_RIGHT = '''
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
        
{operators_init}

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

USER_PROMPT_PART_3_RL_RIGHT = '''
### 6. Problem Domain Examples
'''

USER_PROMPT_PART_4_RL_RIGHT = '''
### 7. Your Response
Now, provide the complete and optimized Python workflow code and thinking based on all the specifications above:'''

PYTHON_START = '''import asyncio
import re
import json
import math
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