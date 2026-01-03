TASK_PROMPT = '''### 1. Problem Domain Overview
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

SYSTEM_PROMPT = '''
Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1. A high-level description of the problem domain
2. A strictly defined set of callable software "Operators" that serve as your only building blocks
3. An illustrative example instance, provided solely to help you understand the abstract reasoning pattern

**Your response MUST strictly adhere to a two-part format: first, a `<think>...</think>` block for your reasoning, followed by a `<code>...</code>` block for the Python solution.**

Your generated Python workflow must be robust enough to work for any problem instance within the described domain.

Crucially, the skill you are developing must be transferable. You should be prepared to receive specifications for **entirely new problem domains and new sets of operators** in the future and apply the same rigorous process of abstraction and generalization.
'''

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

START_PROMPT = '''### 2. Available Operators & Building Blocks

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.

#### 🔑 **CRITICAL: Understanding the `instruction` and `context` Parameters**

Every operator uses a standardized parameter structure that enables powerful, flexible workflows:

**The `instruction` Parameter (Required for all operators):**
- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do
- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous
- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)
- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, detailed reasoning strategies, and formatted requirements
- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded in the workflow structure. While instructions can dynamically incorporate relevant extracted information to guide the operation, the main data to be processed should remain in the context parameter.

**Example of a Rich Instruction:**
```python
instruction = f"""
Extract all numerical values from the passage and identify their context.
For each number found:
1. Record the exact numerical value
2. Identify the entity or concept it's associated with
3. Determine the type (count, year, percentage, score, etc.)
4. Note any modifiers (total, average, difference, etc.)
5. Extract the surrounding sentence for context

Additionally, based on the question type detected earlier: {question_type},
pay special attention to {specific_focus}.

Format your output as a structured list with clear labels.
If calculations are mentioned, show the components separately.
"""
```

**The `context` Parameter (Required for all operators except Generate):**
- **Purpose:** Provides the INPUT DATA that the instruction will operate on
- **Content:** The actual text, data, or results from previous operations - this is the primary information source
- **Type:** String for Generate/Revise/Summarize operators
- **Usage:** Think of it as the "working material" that the instruction processes
- **Note:** Ensemble uses `contexts` (plural) which takes List[str] instead of a single string

---

### Core Operators

**1. Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions
- **When to Use:** Initial analysis, reasoning steps, creating hypotheses, drafting solutions
- **Best Practices:**
  - Write instructions that fully specify the generation task
  - Include step-by-step reasoning requirements in the instruction
  - Can use empty context for initial generation, or provide context from previous steps
  - Consider using f-strings to dynamically build instructions with extracted information

**2. Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria
- **When to Use:** Error correction, iterative refinement, style improvements, accuracy checks
- **Best Practices:**
  - Specify exactly WHAT to improve and HOW in the instruction
  - Can include specific error patterns, accuracy criteria, or style guidelines
  - Consider multiple revision passes with different focus areas
  - The context parameter contains the text to be revised

**3. Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information relevant to the problem
- **When to Use:** Managing long contexts, extracting key points, creating overviews
- **Best Practices:**
  - Use the instruction to specify what aspects to prioritize in the summary
  - Can request specific formats (bullet points, paragraph, key-value pairs)
  - Useful for managing token limits in complex reasoning chains
  - The context parameter contains the text to be summarized

**4. Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions
- **When to Use:** Combining parallel analyses, selecting best answers, voting mechanisms
- **Best Practices:**
  - Provide clear selection or synthesis criteria in the instruction
  - Can implement voting strategies, quality rubrics, or fusion approaches
  - The contexts parameter is a LIST of strings (different from other operators)
  - Consider using detailed decision matrices or scoring systems in the instruction

### 3. Workflow Design Patterns & Strategies

#### 💡 **Dynamic Instruction Construction: The Key Pattern**

The most powerful technique is to extract information early and incorporate it into subsequent instructions:

```python
# Step 1: Extract key information
extraction = await self.generate(
    instruction="""
    Analyze the problem and extract:
    1. All numerical values with their contexts
    2. All entities mentioned (people, places, things)
    3. Any temporal information (dates, sequences, durations)
    4. Relationships between entities
    Format as structured data with clear categories.
    """,
    context=self.problem_text
)

# Step 2: Use extracted info to build a targeted instruction
analysis = await self.generate(
    instruction=f"""
    Based on this extracted information:
    {extraction}
    
    Now solve the problem step by step:
    1. Identify which extracted elements are relevant to the question
    2. Determine what operations or comparisons are needed
    3. Perform any necessary calculations
    4. Verify the logical consistency of your answer
    
    Focus particularly on the numerical relationships and ensure
    all arithmetic is shown explicitly.
    """,
    context=self.problem_text
)

# Step 3: Refine with specific error checking
refined = await self.revise(
    instruction=f"""
    Review this solution for common errors:
    1. Arithmetic mistakes - recalculate all operations
    2. Entity confusion - verify correct entity-number associations
    3. Logic errors - ensure the answer addresses the exact question
    
    The original extraction showed these key values: {extraction}
    Verify the solution uses them correctly.
    """,
    context=analysis
)
```

#### **Foundation Patterns:**

**A. Linear Decomposition**
```python
step1 = await self.generate(
    instruction="Extract and structure all factual information...",
    context=self.problem_text
)
step2 = await self.generate(
    instruction="Based on the extracted facts, identify the core question...",
    context=step1
)
step3 = await self.generate(
    instruction="Solve the identified question using the structured facts...",
    context=step2
)
```

**B. Iterative Refinement**
```python
initial = await self.generate(instruction="...", context="...")
refined1 = await self.revise(
    instruction="Check for arithmetic errors and recalculate...",
    context=initial
)
refined2 = await self.revise(
    instruction="Verify entity associations and relationships...",
    context=refined1
)
```

**C. Parallel Exploration**
```python
import asyncio

# Create diverse approaches WITHOUT await
approach1 = self.generate(
    instruction="Solve using arithmetic approach...",
    context=self.problem_text
)
approach2 = self.generate(
    instruction="Solve using logical deduction...",
    context=self.problem_text
)
approach3 = self.generate(
    instruction="Solve by extracting and comparing...",
    context=self.problem_text
)

# Execute in parallel
results = await asyncio.gather(approach1, approach2, approach3)

# Synthesize results
final = await self.ensemble(
    instruction="Compare the three approaches and select the most reliable answer...",
    contexts=results
)
```

**D. Extract-Analyze-Synthesize Pipeline**
```python
# Extract structured information
extraction = await self.generate(
    instruction="Extract all data points, organize by category...",
    context=self.problem_text
)

# Analyze the structured data
analysis = await self.generate(
    instruction=f"Given this structured data: {extraction}\nPerform required analysis...",
    context=self.problem_text
)

# Synthesize into final answer
synthesis = await self.summarize(
    instruction="Condense the analysis into a clear, concise answer...",
    context=analysis
)
```

#### **Advanced Patterns:**

**E. Multi-Stage Verification**
```python
# Generate initial solution
solution = await self.generate(
    instruction="Solve the problem step by step...",
    context=self.problem_text
)

# Generate verification approaches
verify_tasks = [
    self.generate(
        instruction=f"Verify this solution by reverse calculation: {solution}",
        context=self.problem_text
    ),
    self.generate(
        instruction=f"Check solution logic and assumptions: {solution}",
        context=self.problem_text
    )
]
verifications = await asyncio.gather(*verify_tasks)

# Ensemble to produce verified answer
final = await self.ensemble(
    instruction="If verifications agree, return the solution. If not, identify and resolve discrepancies...",
    contexts=[solution] + verifications
)
```

**F. Adaptive Complexity Handling**
```python
# Assess problem complexity
assessment = await self.generate(
    instruction="Determine if this problem requires: simple extraction, arithmetic, multi-hop reasoning, or complex inference...",
    context=self.problem_text
)

# Branch based on complexity
if "arithmetic" in assessment.lower():
    result = await self.generate(
        instruction="Extract all numbers, identify operations needed, calculate step by step...",
        context=self.problem_text
    )
elif "multi-hop" in assessment.lower():
    # Multi-stage reasoning
    hop1 = await self.generate(
        instruction="Identify and resolve the first reasoning step...",
        context=self.problem_text
    )
    hop2 = await self.generate(
        instruction=f"Building on: {hop1}\nResolve the next reasoning step...",
        context=self.problem_text
    )
    result = await self.generate(
        instruction=f"Combine insights: {hop1} and {hop2}\nProduce final answer...",
        context=self.problem_text
    )
```

#### **🚀 Innovation Guidelines:**

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
# ❌ WRONG: Hardcoding problem-specific information
result = await self.generate(
    instruction="Count how many field goals the Patriots scored",  # Too specific!
    context=self.problem_text
)

# ✅ CORRECT: Generic instruction that works for any problem
result = await self.generate(
    instruction="Identify what the question is asking for, then count or calculate the requested value",
    context=self.problem_text
)

# ❌ WRONG: Sequential execution when parallel is possible
result1 = await self.generate(...)  # Waits
result2 = await self.generate(...)  # Then waits again

# ✅ CORRECT: Parallel execution for independent operations
results = await asyncio.gather(
    self.generate(...),
    self.generate(...)
)
```

### 4. Your Task: Complete the `run_workflow` Method

Your task is to write the Python code for the `run_workflow` method within the provided template. Focus on creating a robust, reusable workflow that leverages detailed instructions.

**Base Template:**
<think>
[Your step-by-step reasoning about the workflow strategy, why you chose specific operators, and how you'll use instructions effectively]
</think>
<code>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem  # Pre-processed problem string
        self.llm = create(config)

        # All operators are initialized and available
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
</code>

### 5. Critical Rules & Constraints

**A. On Generality (Core Principle):**
- **Goal:** Create a strategic template for a CLASS of problems
- **ALLOWED in instructions:** Keywords, patterns, and strategies from the problem domain
- **FORBIDDEN in workflow:** Hardcoded answers or specific passage data

**B. On Instruction Design:**
- **REQUIRED:** Comprehensive instructions that fully specify each operation
- **ENCOURAGED:** Dynamic instruction building with f-strings and extracted information
- **REMEMBER:** Instructions can be 100-500+ words - use this space fully

**C. On Parameter Usage:**
- **All operators require:** `instruction` (str) as first parameter
- **Context parameters:** `context` (str) for Generate/Revise/Summarize, `contexts` (List[str]) for Ensemble
- **Generate:** Can use empty string for context when no prior context exists

**D. On Logic & Control Flow:**
- **Conditions:** Base on operator results, not direct problem_text parsing
- **Parallelism:** Use `asyncio.gather()` for independent operations
- **Branching:** Allowed based on runtime analysis results

**E. On Operator Usage:**
- **Typical complexity:** 3-8 operator calls
- **Each call:** Must contribute meaningfully
- **Efficiency:** Parallelize when possible

**F. Response Format:**
- **MUST contain exactly:**
  1. `<think>...</think>` - Reasoning process
  2. `<code>...</code>` - Complete implementation
- **NO text outside these blocks**

### 6. Illustrative Example(s)

The following concrete examples help you understand the problem type. Remember: create a workflow for the *class* of problems, not just these specific instances.

'''