OPERATOR_PROMPT_PART_1 = '''### Available Operators

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.

**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as "**Original Problem:**" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.

**Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions

**Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria

**Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses text while preserving key information relevant to the problem

**Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts_list: List[str]) -> str`
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions

** Programmer: EXECUTE code solutions**
- **Signature:** `await self.programmer(instruction: str, context: str = "", max_retries: int = 3) -> str`
- **Purpose:** Generates and executes Python code to solve computational problems
- **When to use:** Mathematical calculations, algorithmic problems, data processing, or any task requiring precise computation
- **Parameters:**
  - `instruction`: Programming task specification
  - `context`: Previous analysis or extracted data to inform code generation
  - `max_retries`: Number of attempts if code fails (default: 3)
- **Returns:** Execution results including generated code and output
- **Safety:** Automatically validates code safety and blocks dangerous operations
- **Example usage:** Solving math problems, implementing algorithms, data analysis, pattern matching

** Decompose: BREAK DOWN complexity**
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

OPERATOR_PROMPT_FULL = '''### Available Operators

All operators are pre-initialized with `self.problem_text` and follow a consistent async interface pattern. The problem text is automatically included in each operator's internal prompts as "**Original Problem:**", so you never need to pass it explicitly.

** Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning from scratch based on strategic instructions
- **When to use:** Initial analysis, creating solution attempts, extracting information, classifying problems, or generating new perspectives
- **Parameters:**
  - `instruction`: Detailed directive (100-500 words recommended) specifying exactly what to generate
  - `context`: Additional data from previous steps (use "" for initial calls)
- **Returns:** Unstructured text response following the instruction
- **Example usage:** Problem decomposition, initial solution attempts, extracting key information, generating hypotheses

** Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria
- **When to use:** Correcting errors, improving clarity, adding missing details, adjusting tone/style, or incorporating feedback
- **Parameters:**
  - `instruction`: Specific revision criteria and goals
  - `context`: The text to be revised (required - typically from a previous operator)
- **Returns:** Improved version of the input text
- **Example usage:** Error correction, clarity enhancement, adding rigor to arguments, fixing logical gaps

** Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses lengthy text while preserving key information relevant to solving the problem
- **When to use:** Reducing context size, extracting key points, creating abstracts, or distilling insights from verbose outputs
- **Parameters:**
  - `instruction`: Summarization strategy and focus areas
  - `context`: The text to summarize (typically from previous operations)
- **Returns:** Condensed version preserving essential information
- **Example usage:** Compressing long analyses, extracting key findings, creating executive summaries

** Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts_list: List[str]) -> str`
- **Purpose:** Evaluates, compares, selects from, or merges multiple candidate solutions
- **When to use:** Choosing best solution from alternatives, combining insights from parallel analyses, or building consensus
- **Parameters:**
  - `instruction`: Decision criteria or synthesis strategy
  - `contexts_list`: List of options to process (typically from parallel operations)
- **Returns:** Selected option or synthesized result
- **Note:** This is the only operator using `contexts_list` instead of `context`
- **Example usage:** Selecting best answer from multiple attempts, merging complementary solutions, voting mechanisms

** Programmer: EXECUTE code solutions**
- **Signature:** `await self.programmer(instruction: str, context: str = "", max_retries: int = 3) -> str`
- **Purpose:** Generates and executes Python code to solve computational problems
- **When to use:** Mathematical calculations, algorithmic problems, data processing, or any task requiring precise computation
- **Parameters:**
  - `instruction`: Programming task specification
  - `context`: Previous analysis or extracted data to inform code generation
  - `max_retries`: Number of attempts if code fails (default: 3)
- **Returns:** Execution results including generated code and output
- **Safety:** Automatically validates code safety and blocks dangerous operations
- **Example usage:** Solving math problems, implementing algorithms, data analysis, pattern matching

** Decompose: BREAK DOWN complexity**
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

#### Important Implementation Notes

- All operators are async and must be called with `await`
- The problem text is always available internally - never pass it as context
- Use empty string `""` for context when starting fresh
- Pass previous outputs as context to chain operations
- Use `asyncio.gather()` to parallelize independent operations
- Ensemble is special: it takes `contexts_list` (List[str]) not `context` (str)'''

OPERATOR_PROMPT_SIMPLE_START = '''### Available Operators

All operators are pre-initialized with `self.problem_text` and follow a consistent async interface pattern. The problem text is automatically included in each operator's internal prompts as "**Original Problem:**", so you never need to pass it explicitly.

#### Important Implementation Notes

- All operators are async and must be called with `await`
- The problem text is always available internally - never pass it as context
- Use empty string `""` for context when starting fresh
- Pass previous outputs as context to chain operations
- Use `asyncio.gather()` to parallelize independent operations
- Ensemble is special: it takes `contexts_list` (List[str]) not `context` (str)'''

generate = '''
** Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Purpose:** Produces new text, analysis, or reasoning from scratch based on strategic instructions
- **When to use:** Initial analysis, creating solution attempts, extracting information, classifying problems, or generating new perspectives
- **Parameters:**
  - `instruction`: Detailed directive (100-500 words recommended) specifying exactly what to generate
  - `context`: Additional data from previous steps (use "" for initial calls)
- **Returns:** Unstructured text response following the instruction
- **Example usage:** Problem decomposition, initial solution attempts, extracting key information, generating hypotheses
'''

revise = '''
** Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Purpose:** Critiques and refines existing text based on specific improvement criteria
- **When to use:** Correcting errors, improving clarity, adding missing details, adjusting tone/style, or incorporating feedback
- **Parameters:**
  - `instruction`: Specific revision criteria and goals
  - `context`: The text to be revised (required - typically from a previous operator)
- **Returns:** Improved version of the input text
- **Example usage:** Error correction, clarity enhancement, adding rigor to arguments, fixing logical gaps
'''

summarize = '''
** Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Purpose:** Condenses lengthy text while preserving key information relevant to solving the problem
- **When to use:** Reducing context size, extracting key points, creating abstracts, or distilling insights from verbose outputs
- **Parameters:**
  - `instruction`: Summarization strategy and focus areas
  - `context`: The text to summarize (typically from previous operations)
- **Returns:** Condensed version preserving essential information
- **Example usage:** Compressing long analyses, extracting key findings, creating executive summaries
'''

ensemble = '''
** Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts_list: List[str]) -> str`
- **Purpose:** Evaluates, compares, selects from, or merges multiple candidate solutions
- **When to use:** Choosing best solution from alternatives, combining insights from parallel analyses, or building consensus
- **Parameters:**
  - `instruction`: Decision criteria or synthesis strategy
  - `contexts_list`: List of options to process (typically from parallel operations)
- **Returns:** Selected option or synthesized result
- **Note:** This is the only operator using `contexts_list` instead of `context`
- **Example usage:** Selecting best answer from multiple attempts, merging complementary solutions, voting mechanisms
'''

programm = '''
** Programmer: EXECUTE code solutions**
- **Signature:** `await self.programmer(instruction: str, context: str = "", max_retries: int = 3) -> str`
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

decompose = '''
** Decompose: BREAK DOWN complexity**
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
- **Key Principle:** Instructions tell the operator HOW to process, WHAT to look for, and WHAT strategy to apply

**The `context` Parameter (Required for all operators except `Ensemble`):**
- **Purpose:** Provides ADDITIONAL working data beyond the original problem (which is already available)
- **Content:** Results from previous operations, intermediate analyses, or extracted information
- **Type:** String for Generate/Revise/Summarize operators
- **IMPORTANT:** Do NOT pass self.problem_text here - it's already available internally to every operator!
- **Common Uses:**
  - Empty string "" for initial Generate calls that only need the problem
  - Previous operator's output for chaining operations
  - Extracted/processed data from earlier steps

**The `contexts_list` Parameter (Only for Ensemble):**
- **Purpose:** Multiple candidate solutions or analyses to compare/synthesize
- **Type:** List[str] - a list of strings from parallel operations

### Understanding Context vs Problem Text

**Key Insight:** Every operator automatically has access to `self.problem_text` internally (you'll see it as "**Original Problem:**" in their prompts). The `context` parameter is for ADDITIONAL data you want to pass between operations.

**Examples of correct context usage:**

```python
# CORRECT: Empty context for initial analysis (problem_text is already available internally)
initial_analysis = await self.generate(
    instruction="Analyze the problem structure and identify key components...",
    context=""  # Empty because we're starting fresh, problem_text is already there
)

# CORRECT: Passing results between operations
refined = await self.revise(
    instruction="Improve clarity and add specific calculations...",
    context=initial_analysis  # Previous step's output becomes new context
)

# WRONG: Redundantly passing problem_text
result = await self.generate(
    instruction="Solve the problem",
    context=self.problem_text  # DON'T DO THIS - already available internally!
)
```

### Workflow Data Flow Pattern

Think of the data flow like this:
1. **Problem text:** Always available to every operator (built-in)
2. **Context:** The "working material" that flows between operators
3. **Instruction:** The strategic directive for how to process

```python
# Typical workflow pattern
step1 = await self.generate(
    instruction="Extract key information and structure...",
    context=""  # Start with empty context
)

step2 = await self.generate(
    instruction=f"Using the extracted structure: {step1}\nNow develop solution...",
    context=step1  # Pass previous result as context
)

step3 = await self.revise(
    instruction="Verify calculations and improve clarity...",
    context=step2  # Continue passing results forward
)
```
```

Additionally, I'd suggest updating the example in the "Common Pitfalls" section to include this specific issue:

```python
# WRONG: Redundantly passing problem_text as context
result = await self.generate(
    instruction="Analyze the problem",
    context=self.problem_text  # Redundant! problem_text is already available internally
)

# CORRECT: Use empty context when starting fresh
result = await self.generate(
    instruction="Analyze the problem",
    context=""  # Empty context - the operator already has problem_text
)

# CORRECT: Pass previous results as context
analysis = await self.generate(
    instruction="Identify key components",
    context=""
)
solution = await self.generate(
    instruction="Build solution based on identified components",
    context=analysis  # Pass the analysis result forward
)

### Workflow Architecture Patterns

#### Foundation Patterns (Building Blocks)
These are the atomic patterns that can be combined in creative ways:

**1. Sequential Chain** - Information flows linearly
**2. Parallel Fork** - Multiple independent processes
**3. Conditional Branch** - Decision-based paths
**4. Iterative Loop** - Refinement through repetition
**5. Hierarchical Decomposition** - Break into sub-problems

#### Advanced Compositions (Combine Foundation Patterns)
Now, let's see how these basics combine into powerful structures:

**Diamond Pattern (Fork → Process → Merge):**
```python
# Generate multiple perspectives, process each, then synthesize
perspectives = await asyncio.gather(
    self.generate(instruction="Analyze from mathematical angle...", context=""),
    self.generate(instruction="Analyze from logical angle...", context=""),
    self.generate(instruction="Analyze from practical angle...", context="")
)
processed = await asyncio.gather(
    *[self.revise(instruction=f"Deepen analysis...", context=p) for p in perspectives]
)
synthesis = await self.ensemble(
    instruction="Synthesize all perspectives into unified understanding",
    contexts_list=processed
)
```

**Cascade with Feedback (Sequential + Loop):**
```python
# Each step validates and potentially triggers re-computation
result = await self.generate(instruction="Initial attempt", context="")
for i in range(3):
    validation = await self.generate(
        instruction=f"Validate step {i+1} output",
        context=result
    )
    if "error" in validation.lower():
        result = await self.revise(
            instruction=f"Fix issues: {validation}",
            context=result
        )
    else:
        break
```

**Tree Search Pattern (Hierarchical + Parallel):**
```python
# Explore solution space like a tree
root = await self.generate(instruction="Identify main approaches", context="")
branches = await asyncio.gather(
    *[self.generate(
        instruction=f"Explore approach: {approach}",
        context=""
    ) for approach in root.split('\n')]
)
best_path = await self.ensemble(
    instruction="Select most promising path",
    contexts_list=branches
)
```

#### Innovation Space (Your Creative Playground)

Beyond these patterns, consider inventing your own architectures:

**Questions to Spark Innovation:**
- What if operators could dynamically spawn new operators based on results?
- How might you implement a "tournament" where solutions compete?
- Could you create a "memory" by accumulating context across iterations?
- What about probabilistic branching based on confidence scores?
- How would you design self-correcting workflows that learn from errors?

**Experimental Pattern Ideas:**
- **Spiral Refinement**: Alternating between broadening (explore) and narrowing (exploit)
- **Consensus Building**: Multiple agents vote on best approach
- **Adversarial Validation**: One path generates, another critiques
- **Adaptive Depth**: Simple problems get simple workflows, complex ones trigger deeper analysis
- **Context Weaving**: Build a rich context tapestry by interleaving different analyses

Remember: The best workflows often combine patterns in unexpected ways. A diamond pattern inside a loop, or parallel branches that each use different iteration strategies. The architecture should emerge from the problem's nature, not be forced into predetermined molds.
```

**Conditional Branching:**
```python
# Analyze problem type
analysis = await self.generate(
    instruction="""Classify this problem:
    1. Is it numerical, logical, or textual?
    2. Does it require exact calculation or estimation?
    3. Are there multiple valid approaches?
    4. What's the expected answer format?
    Provide structured classification.""",
    context=""
)

# Branch based on problem type
if "numerical" in analysis.lower() and "exact" in analysis.lower():
    result = await self.generate(
        instruction="""Solve with precise mathematical computation:
        - Show all algebraic steps
        - Maintain full precision
        - Double-check arithmetic
        - Present final answer with appropriate units""",
        context=""
    )
elif "estimation" in analysis.lower():
    estimates = await asyncio.gather(
        self.generate(instruction="Estimate using order of magnitude...", context=""),
        self.generate(instruction="Estimate using dimensional analysis...", context=""),
        self.generate(instruction="Estimate using comparable examples...", context="")
    )
    result = await self.ensemble(
        instruction="Synthesize estimates into best approximation",
        contexts_list=estimates
    )
else:
    # Default comprehensive approach
    result = await self.generate(
        instruction="Apply general problem-solving framework...",
        context=""
    )
```

**Dynamic Context Building:**
```python
# Extract key information progressively
entities = await self.generate(
    instruction="""Extract all named entities, numbers, and relationships:
    Format as structured list with categories:
    - People: [names and roles]
    - Places: [locations and contexts]
    - Numbers: [values and what they represent]
    - Actions: [what happens and when]""",
    context=""
)

constraints = await self.generate(
    instruction=f"""Given these entities:
    {entities}
    
    Now identify all constraints and conditions:
    - Explicit constraints stated in problem
    - Implicit constraints from context
    - Physical or logical limitations
    - Boundary conditions""",
    context=entities  # Build on previous extraction
)

solution_space = await self.generate(
    instruction=f"""With entities and constraints identified:
    Entities: {entities}
    Constraints: {constraints}
    
    Define the solution space:
    - What are we solving for?
    - What methods are applicable?
    - What would constitute a valid answer?""",
    context=f"{entities}\n\n{constraints}"  # Cumulative context
)
```
'''


USER_PROMPT_LONG ='''### Your Task: Design a Sophisticated Workflow

Create a workflow that demonstrates **architectural sophistication** and **strategic diversity**. Your workflow should NOT be a simple linear sequence.

**Response Format:**

1. **Deep Reasoning Phase** (`<think>` block):
   - Write **at least 800 words** of thoughtful analysis (aim for 1000-1500 words)
   - Don't follow a template - let your reasoning flow naturally
   - Consider multiple perspectives and trade-offs
   - Question assumptions and explore alternatives
   - Think about edge cases and failure modes
   - Discuss why certain approaches might NOT work
   - Consider computational efficiency vs accuracy trade-offs
   - Reflect on how your design handles uncertainty
   
   Your thinking should be genuinely exploratory - like solving a puzzle where you're discovering the solution as you think, not just listing predetermined steps. Show the evolution of your ideas, including dead ends and pivots.

2. **Implementation Phase** (```python``` code block):
   - Transform your insights into elegant, working code
   - The code should reflect the sophistication of your thinking

**Base Template:**
```
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
        
{operators_init}

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
```
#### Architectural Innovation Challenge

**Level 1 (Minimum)**: Use at least one parallel operation and one conditional branch
**Level 2 (Good)**: Combine 3+ patterns in a non-trivial way
**Level 3 (Excellent)**: Create a novel architecture pattern we haven't shown
**Level 4 (Outstanding)**: Design a self-adaptive workflow that changes strategy based on intermediate results

**Innovation Indicators We Love to See:**
- Workflows that "think about thinking" (meta-cognition)
- Dynamic instruction generation that evolves based on discoveries
- Creative use of context accumulation and transformation
- Unexpected operator combinations that create emergent capabilities
- Elegant handling of edge cases through architectural choices

**Remember**: We're not looking for complexity for its own sake, but rather sophisticated simplicity - architectures that are both powerful and elegant. Sometimes the most innovative solution is finding a surprisingly simple way to handle complex problems.

Your workflow should feel like a living system that adapts and responds, not a rigid pipeline. Think of it as choreographing a dance between operators, where each movement flows naturally from the last while building toward a crescendo of insight.

**Critical Rules:**
1. Generality: The workflow must be generic enough to handle ANY problem instance from the described domain, not just the provided examples.
2. Instructions: Use comprehensive, detailed instructions (100-500+ words OK)
3. Parameters: `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble
4. Control Flow: Branch on operator results, not direct problem_text parsing
5. Complexity: Typically 3-8 operator calls, parallelize when possible

**Performance Considerations:**
- Parallel operations (`asyncio.gather`) are computationally efficient but use more API calls
- Deep iteration loops may increase latency - balance depth with practicality
- Context accumulation should be strategic - avoid redundant information buildup
- Consider early termination conditions for iterative patterns'''

USER_PROMPT_SHORT ='''### Your Task: Complete the `run_workflow` Method

Your task is to write the Python code for the `run_workflow` method within the provided template below. Focus on creating a robust, reusable workflow that leverages detailed instructions.

**Response Format:**
1. Provide your reasoning in a `<think>...</think>` block
2. Include a ```python``` code block with the complete workflow implementation

**Base Template:**
```
<think>
Design a universal workflow for this problem domain. Consider:
- Core patterns and variations across the domain
- Multiple solution strategies and their trade-offs
- For each operator in your workflow: why it's necessary, how to craft its instructions, and how it connects with other operators
- How your design ensures the workflow solves ANY problem in this domain (not just the examples shown)
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
        
{operators_init}

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
```
'''

generate_init = '''self.generate = operator.Generate(self.llm, self.problem_text)'''
revise_init = '''self.revise = operator.Revise(self.llm, self.problem_text)'''
summarize_init = '''self.summarize = operator.Summarize(self.llm, self.problem_text)'''
ensemble_init = '''self.ensemble = operator.Ensemble(self.llm, self.problem_text)'''
programm_init = '''self.programmer = operator.Programmer(self.llm, self.problem_text)'''
decompose_init = '''self.decompose = operator.Decompose(self.llm, self.problem_text)'''


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