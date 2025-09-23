# Workflow ID: mgsmbn_79_0
# Benchmark: mgsmbn
# Data Indices: [128, 104]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # PHASE 1: SEMANTIC PARSING & PROBLEM CLASSIFICATION
        initial_analysis = await self.generate(
            instruction="""Perform deep semantic parsing of this Bengali math problem. Your task:

1. Extract ALL named entities (people, objects, places) and categorize them.
2. Identify EVERY numerical value and explicitly state what it quantifies (e.g., "4টি কলম" → quantity: 4, object: pen).
3. Map ALL relationships between entities and values (e.g., "প্রতিটির দাম $1.5" → price per unit).
4. Classify the problem type: Sequential, Proportional, Distribution, Comparison, or Multi-entity.
5. Identify any implicit constraints (e.g., non-negative quantities, whole numbers for countable items).
6. Flag any ambiguous phrases that might need clarification.

Output in this structured format:
{
  "entities": [{"name": "...", "type": "...", "role": "..."}],
  "quantities": [{"value": ..., "unit": "...", "applies_to": "..."}],
  "relationships": [{"source": "...", "target": "...", "operation": "..."}],
  "problem_type": "...",
  "constraints": [...],
  "ambiguities": [...]
}""",
            context=""
        )

        # PHASE 2: ITERATIVE DECOMPOSITION & VALIDATION
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, independent subproblems. Each subproblem must:
- Be solvable with basic arithmetic or algebra
- Have clearly defined inputs and expected outputs
- Include any necessary unit conversions
- Reference prerequisite subproblems if dependencies exist
- Preserve real-world constraints (no negative items, etc.)

Structure each subproblem as:
{
  "id": "step_X",
  "description": "What needs to be calculated",
  "inputs": ["list", "of", "required", "values"],
  "operation": "add/subtract/multiply/divide/algebraic",
  "output": "expected result with unit",
  "dependencies": ["step_Y", "step_Z"]
}""",
            context=initial_analysis
        )

        # Validate and refine decomposition
        validated_decomposition = await self.revise(
            instruction=f"""Critically review this decomposition:

1. Check that EVERY quantity from initial analysis is used in at least one subproblem.
2. Verify that relationships are correctly translated into operations.
3. Ensure dependencies are properly ordered (no circular dependencies).
4. Confirm units are consistent across related subproblems.
5. Add any missing subproblems for implicit calculations (e.g., unit conversions).
6. Simplify overly complex subproblems by splitting them.

Original analysis for reference:
{initial_analysis}

Output the revised decomposition in the same JSON-compatible format.""",
            context=json.dumps(decomposition)
        )

        # PHASE 3: PARALLEL SOLUTION STRATEGIES
        # Generate multiple solution approaches simultaneously
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a complete solution strategy using DIRECT COMPUTATION:
- Solve subproblems in dependency order
- Show intermediate results with units
- Handle unit conversions explicitly
- Final answer must be a single numerical value

Use this decomposition:
{validated_decomposition}

Output as executable steps with calculations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a complete solution strategy using ALGEBRAIC MODELING:
- Define variables for unknowns
- Write equations based on relationships
- Solve system of equations
- Substitute known values
- Final answer must be a single numerical value

Use this decomposition:
{validated_decomposition}

Output as mathematical expressions with substitutions.""",
                context=""
            )
        ]
        
        direct_solution, algebraic_solution = await asyncio.gather(*strategy_tasks)

        # PHASE 4: CODE EXECUTION & VALIDATION
        # Convert best strategy to executable code
        code_execution = await self.programmer(
            instruction=f"""Generate Python code that computes the final answer based on this solution strategy:

{direct_solution}

Requirements:
- Use clear variable names matching entities
- Include all intermediate calculations
- Handle units as comments
- Return ONLY the final numerical answer
- Validate against constraints (no negatives, etc.)
- If error occurs, return -1

Example structure:
# Calculate pen cost: 4 pens × $1.5 each
pen_cost = 4 * 1.5
# Calculate notebook cost: 2 notebooks × $4 each  
notebook_cost = 2 * 4
# Total cost
total = pen_cost + notebook_cost + 20  # bond paper cost
print(total)""",
            context=direct_solution,
            max_retries=3
        )

        # PHASE 5: CONSENSUS & FINAL VALIDATION
        final_answer = await self.ensemble(
            instruction="""Select the most reliable answer from these candidates:
1. Code execution result
2. Direct computation strategy
3. Algebraic modeling strategy

Criteria:
- Prefer code execution if available and valid (not -1)
- If code failed, choose between direct and algebraic based on:
  a) Completeness of steps
  b) Consistency with problem constraints
  c) Mathematical correctness
- Final output must be ONLY the numerical answer (no units, no text)

Candidates:
CODE RESULT: {code_execution}
DIRECT: {direct_solution}
ALGEBRAIC: {algebraic_solution}""",
            contexts_list=[code_execution, direct_solution, algebraic_solution]
        )

        # Final sanity check
        final_validated = await self.revise(
            instruction="""Perform final validation:
1. Is the answer a single numerical value?
2. Does it satisfy all problem constraints (non-negative, reasonable magnitude)?
3. Does it match at least one of the solution strategies?
4. If answer seems unreasonable, return "ERROR"

Output ONLY the final numerical answer or "ERROR".""",
            context=final_answer
        )

        return final_validated