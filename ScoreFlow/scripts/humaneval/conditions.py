TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **HumanEval benchmark**. These problems test the ability to generate correct Python functions from detailed docstrings and function signatures.

**Core Characteristics:**
- **Input:** Function signature with comprehensive docstring describing the task, including examples
- **Required Skills:** Understanding docstring specifications, algorithm design, Python syntax, edge case handling
- **Answer Type:** Complete executable Python function implementation
- **Validation:** Must pass test cases wrapped in a `check(candidate)` function

**Common Problem Types:**
- **String Manipulation:** Pattern matching, parsing, transformation, validation
- **Mathematical Operations:** Number theory, arithmetic sequences, special calculations
- **List/Array Processing:** Sorting, filtering, searching, transformation algorithms
- **Logic Problems:** Conditional logic, state machines, decision trees
- **Data Structure Manipulation:** Working with nested structures, trees, custom sequences
- **Algorithm Implementation:** Classic algorithms, optimizations, recursive solutions

**Critical Challenges:**
- **Docstring Interpretation:** Must carefully parse examples and edge cases from docstring
- **Type Inference:** Function signature may not specify types explicitly
- **Edge Cases:** Examples in docstring often hint at special cases to handle
- **Performance Considerations:** Some problems have implicit efficiency requirements
- **Return Type Consistency:** Must match exact format expected by tests (e.g., float vs int)
- **Recursive Definitions:** Some problems define recursive relationships that need careful implementation

**Key Success Factors:**
- Carefully analyzing ALL examples in the docstring
- Understanding the mathematical or logical pattern from examples
- Implementing exactly what the docstring specifies (not over-engineering)
- Matching the exact function signature provided
- Handling edge cases mentioned or implied in examples
- Ensuring correct return types (especially float vs int distinctions)

**Common Pitfalls:**
- Misunderstanding the problem from incomplete reading of docstring
- Missing edge cases that are shown in examples but not explicitly stated
- Type errors (returning int when float is expected or vice versa)
- Off-by-one errors in sequences or ranges
- Not handling the base cases in recursive problems correctly
- Over-complicating simple problems

**HumanEval-Specific Considerations:**
- **Docstring is King:** The docstring contains ALL the specification - read it completely
- **Examples are Test Cases:** The examples in docstring often become the test cases
- **Function Signature Given:** The exact function name and parameters are provided
- **Check Function Format:** Tests are wrapped in `check(candidate)` where candidate is your function

**CRITICAL Workflow Design Considerations for HumanEval:**

### ⚠️ Understanding Operator Return Types (MUST READ!)
**ALL operators (Generate, Revise, Summarize, Ensemble) ALWAYS return STRINGS, never structured data!**

✅ **RECOMMENDED HumanEval Workflow Pattern:**
```python
async def run_workflow(self):
    import asyncio
    
    # Step 1: Extract function name (it's given in the prompt)
    func_name = await self.generate(
        instruction="Extract ONLY the function name from the def statement. Return just the name, nothing else.",
        context=""
    )
    
    # Step 2: Analyze the docstring examples
    analysis = await self.generate(
        instruction="""
        Analyze the docstring and examples carefully:
        1. What pattern do the examples show?
        2. What are the edge cases?
        3. What is the expected return type?
        Return a brief analysis in 2-3 sentences.
        """,
        context=""
    )
    
    # Step 3: Generate solution with comprehensive instructions
    solution = await self.generate(
        instruction=f"""
        Implement the function '{func_name}' based on the docstring specification.
        Analysis: {analysis}
        
        Requirements:
        1. Follow the EXACT function signature provided
        2. Implement the logic that satisfies ALL examples in the docstring
        3. Handle edge cases shown in examples
        4. Return the correct type (int, float, list, etc.) as shown in examples
        5. Include any necessary imports at the top
        6. Return ONLY the Python code, no explanations
        """,
        context=""
    )
    
    return solution
```

'''

SYSTEM_PROMPT = '''\nYour fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.\n\nYour core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:\n1. A high-level description of the problem domain\n2. A strictly defined set of callable software \"Operators\" that serve as your only building blocks\n3. An illustrative example instance, provided solely to help you understand the abstract reasoning pattern\n\n**Your response MUST strictly adhere to the following two-part format:**\n\n**1. A `<think>...</think>` block:**\nInside this block, you must articulate your complete reasoning process for creating a **general solution for the entire problem class**, not just the provided example. Your reasoning should include:\n- A step-by-step analysis of the problem category.\n- Consideration of different potential strategies and approaches.\n- A clear explanation of your final design decisions and why you chose specific operators for the workflow.\n\n**2. A Python Code Block:**\nImmediately following the closing `</think>` tag, provide the complete and reusable Python solution. This code must be enclosed in markdown fences, specifically ` ```python ... ``` `.\n\n---\n\n### Example Response Structure:\n\n<think>\nFirst, I need to deeply understand the core characteristics of this problem class. The goal is to design a workflow that is robust and generic.\n\nMy strategy will be to [Your step-by-step reasoning for the general problem class goes here...].\n\nI've chosen the `Generate` operator for the initial step because [Your design decision explanation...]. This approach is superior to [alternative approach] because [justification...].\n</think>\n```python\n# --- DO NOT IMPORT HERE ---\nclass Workflow:\n    def __init__(self, config, problem) -> None:\n        # --- DO NOT MODIFY THIS SECTION ---\n        self.config = config\n        self.problem_text = problem\n        self.llm = create(config)\n        \n        self.generate = operator.Generate(self.llm, self.problem_text)\n        self.revise = operator.Revise(self.llm, self.problem_text)\n        self.summarize = operator.Summarize(self.llm, self.problem_text)\n        self.ensemble = operator.Ensemble(self.llm, self.problem_text)\n\n    async def run_workflow(self):\n        \"\"\"\n        Implement the core problem-solving logic here.\n        Remember: \n        - Use detailed, comprehensive instructions\n        - Dynamic instruction construction is powerful\n        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]\n        \"\"\"\n        import asyncio\n        # --- YOUR WORKFLOW LOGIC HERE ---\n```\n---\n\nYour generated Python workflow must be robust enough to work for any problem instance within the described domain.'''

PYTHON_START = '''import asyncio
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

START_PROMPT = '''\n### 2. Available Operators & Building Blocks\n\nAll operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.\n\n**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as \"**Original Problem:**\" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.\n\n\n#### **CRITICAL: Understanding Parameters**\n\n**The `instruction` Parameter (Required for all operators):**\n- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do\n- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous\n- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)\n- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, detailed reasoning strategies, and formatted requirements\n- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded in the workflow structure. While instructions can dynamically incorporate relevant extracted information to guide the operation, the main data to be processed should remain in the context parameter.\n\n**The `context` Parameter (Required for all operators except Generate):**\n- **Purpose:** Provides the INPUT DATA that the instruction will operate on\n- **Content:** The actual text, data, or results from previous operations - this is the primary information source\n- **Type:** String for Generate/Revise/Summarize operators\n- **Usage:** Think of it as the \"working material\" that the instruction processes\n- **Note:** Ensemble uses `contexts` (plural) which takes List[str] instead of a single string\n\n### Core Operators\n\n**1. Generate: CREATE new information**\n- **Signature:** `await self.generate(instruction: str, context: str = \"\") -> str`\n- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions\n\n**2. Revise: IMPROVE existing information**\n- **Signature:** `await self.revise(instruction: str, context: str) -> str`\n- **Purpose:** Critiques and refines existing text based on specific improvement criteria\n\n**3. Summarize: COMPRESS information**\n- **Signature:** `await self.summarize(instruction: str, context: str) -> str`\n- **Purpose:** Condenses text while preserving key information relevant to the problem\n\n**4. Ensemble: DECIDE between or synthesize options**\n- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`\n- **Purpose:** Evaluates, compares, or merges multiple candidate solutions\n\n### 3. Key Design Principles\n\n**Dynamic Instruction Construction:**\nExtract information early, then incorporate it into subsequent instructions using f-strings:\n```python\nextraction = await self.generate(instruction=\"Extract all numerical values...\", context=self.problem_text)\nanalysis = await self.generate(\n    instruction=f\"Given these extracted values: {extraction}\\nNow solve step by step...\",\n    context=self.problem_text\n)\n```\n\n**Parallel Execution:**\nUse `asyncio.gather()` for independent operations:\n```python\nresults = await asyncio.gather(\n    self.generate(instruction=\"Approach 1...\", context=...),\n    self.generate(instruction=\"Approach 2...\", context=...)\n)\nfinal = await self.ensemble(instruction=\"Select best...\", contexts=results)\n```\n\n**Common Pitfalls:**\n- Don't hardcode problem-specific data in workflow code\n- Don't use `await` inside list comprehensions (blocks parallelism)\n- Do use detailed instructions (100-500+ words when needed)\n- Do extract info dynamically and incorporate into instructions\n\n#### **Innovation Guidelines:**\n\n**Maximize the power of instructions by:**\n- Building multi-paragraph instructions that leave nothing to interpretation\n- Dynamically incorporating ALL relevant extracted information\n- Creating instruction templates that adapt based on detected patterns\n- Using instructions to implement complex reasoning strategies\n- Including specific formatting requirements and output structures\n\n**Remember:**\n- Instructions are mini-prompts - make them as detailed as needed\n- Extract early, enrich instructions throughout\n- The workflow provides structure; instructions provide intelligence\n- Never hardcode problem-specific data in the workflow code itself\n- Always pass context appropriately - empty string for initial Generate, List for Ensemble\n\n#### **Common Pitfalls to Avoid:**\n\n```python\n# WRONG: Hardcoding problem-specific information\nresult = await self.generate(\n    instruction=\"Count how many field goals the Patriots scored\",  # Too specific!\n    context=self.problem_text\n)\n\n# CORRECT: Generic instruction that works for any problem\nresult = await self.generate(\n    instruction=\"Identify what the question is asking for, then count or calculate the requested value\",\n    context=self.problem_text\n)\n\n# WRONG: Sequential execution when parallel is possible\nresult1 = await self.generate(...)  # Waits\nresult2 = await self.generate(...)  # Then waits again\n\n# CORRECT: Parallel execution for independent operations\nresults = await asyncio.gather(\n    self.generate(...),\n    self.generate(...)\n)\n```\n\n### 4. Your Task: Complete the `run_workflow` Method\n\nYour task is to write the Python code for the `run_workflow` method within the provided template. Focus on creating a robust, reusable workflow that leverages detailed instructions.\n\n**Base Template:**\n\n<think>\nFirst, I need to deeply understand the core characteristics of this problem class. The goal is to design a workflow that is robust and generic.\n\nMy strategy will be to [Your step-by-step reasoning for the general problem class goes here...].\n\nI've chosen the `Generate` operator for the initial step because [Your design decision explanation...]. This approach is superior to [alternative approach] because [justification...].\n</think>\n```python\n# --- DO NOT IMPORT HERE ---\nclass Workflow:\n    def __init__(self, config, problem) -> None:\n        # --- DO NOT MODIFY THIS SECTION ---\n        self.config = config\n        self.problem_text = problem\n        self.llm = create(config)\n        \n        self.generate = operator.Generate(self.llm, self.problem_text)\n        self.revise = operator.Revise(self.llm, self.problem_text)\n        self.summarize = operator.Summarize(self.llm, self.problem_text)\n        self.ensemble = operator.Ensemble(self.llm, self.problem_text)\n\n    async def run_workflow(self):\n        \"\"\"\n        Implement the core problem-solving logic here.\n        Remember: \n        - Use detailed, comprehensive instructions\n        - Dynamic instruction construction is powerful\n        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]\n        \"\"\"\n        import asyncio\n        # --- YOUR WORKFLOW LOGIC HERE ---\n```\n\n### 5. Critical Rules\n\n**A. Generality:** Create templates for problem CLASSES, not specific instances\n**B. Instructions:** Use comprehensive, detailed instructions (100-500+ words OK)\n**C. Parameters:** `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble\n**D. Control Flow:** Branch on operator results, not direct problem_text parsing\n**E. Complexity:** Typically 3-8 operator calls, parallelize when possible\n**F. Response Format:** ONLY `<think>...</think>` followed by ` ```python ... ``` `\n\n'''
