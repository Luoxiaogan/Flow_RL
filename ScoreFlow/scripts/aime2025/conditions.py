TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **AIME 2025 benchmark** (American Invitational Mathematics Examination 2025). These are advanced mathematical problems designed for high-achieving high school students.

**Core Characteristics:**
- **Input:** Complex mathematical problems involving geometry, number theory, algebra, combinatorics, and probability
- **Required Skills:** Advanced mathematical reasoning, proof techniques, optimization, complex calculations
- **Answer Type:** Typically an integer between 000 and 999

**Common Problem Types:**
- **Geometric Problems:** 3D geometry, complex figure analysis, coordinate geometry
- **Number Theory:** Modular arithmetic, divisibility, prime factorization, Diophantine equations
- **Combinatorics:** Counting principles, probability, permutations, combinations
- **Algebraic Problems:** Polynomial equations, complex numbers, functional equations
- **Optimization:** Finding maxima/minima, extremal problems, inequalities
- **Sequence and Series:** Recursive sequences, generating functions, summations

**Mathematical Techniques:**
- Advanced algebraic manipulation
- Trigonometric identities and complex number operations
- Coordinate geometry and vector calculations
- Mathematical induction and proof by contradiction
- Calculus techniques (when applicable)
- Combinatorial arguments and counting strategies

**Critical Challenges:**
- **Multi-step Reasoning:** Problems often require 5-10+ interconnected steps
- **Creative Insights:** May need non-obvious approaches or transformations
- **Precision Requirements:** Exact integer answers, no approximations allowed
- **Complex Notation:** Heavy use of mathematical symbols and formal notation
- **Time Complexity:** Problems designed to be challenging even with ample time

**Key Success Factors:**
- Breaking down complex problems into manageable sub-problems
- Exploring multiple solution approaches in parallel
- Rigorous verification of intermediate results
- Clear tracking of all variables and constraints
- Systematic exploration of special cases
- Careful attention to problem boundaries and edge cases

'''

SYSTEM_PROMPT = '''\nYour fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

You are dealing with AIME-level mathematics problems that require sophisticated mathematical reasoning and multi-step solutions.

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
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio
        # --- YOUR WORKFLOW LOGIC HERE ---
```
---

Your generated Python workflow must be robust enough to work for any problem instance within the described domain.'''

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
            # Error details are defined and used here, not exposed to external .format()
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred during workflow execution. Details: {{escaped_error_details}}"
'''

START_PROMPT = '''\n### 2. Available Operators & Building Blocks

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
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions

### 3. Key Design Principles

**Dynamic Instruction Construction:**
Extract information early, then incorporate it into subsequent instructions using f-strings:
```python
extraction = await self.generate(instruction="Extract all mathematical constraints...", context=self.problem_text)
analysis = await self.generate(
    instruction=f"Given these constraints: {extraction}\\nNow solve step by step...",
    context=self.problem_text
)
```

**Parallel Execution:**
Use `asyncio.gather()` for independent operations:
```python
results = await asyncio.gather(
    self.generate(instruction="Approach using algebraic methods...", context=...),
    self.generate(instruction="Approach using geometric insights...", context=...)
)
final = await self.ensemble(instruction="Select best approach...", contexts=results)
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
    instruction="Find the value when z=4+3i",  # Too specific!
    context=self.problem_text
)

# CORRECT: Generic instruction that works for any problem
result = await self.generate(
    instruction="Identify all given constraints and values in the problem, then set up the mathematical framework",
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