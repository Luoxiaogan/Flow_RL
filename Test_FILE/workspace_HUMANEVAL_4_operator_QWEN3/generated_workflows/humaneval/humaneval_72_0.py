# Workflow ID: humaneval_72_0
# Benchmark: humaneval
# Data Indices: [115, 34]

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
        Universal code generation workflow with spiral validation and parallel strategy synthesis.
        Handles any function-from-specification problem in the domain.
        """
        import asyncio
        import re

        # PHASE 1: PROBLEM DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Perform deep structural analysis of the code generation problem. Extract and structure:

1. FUNCTION SIGNATURE: Identify exact function name and parameters from ENTRY POINT and signature.
2. INPUT/OUTPUT SPEC: Determine expected types, structures, and constraints from examples.
3. SEMANTIC DOMAIN: Classify problem type (mathematical, set operations, string manipulation, algorithmic, etc.).
4. KEY OPERATIONS: List required operations (sum, sort, unique, ceil, regex, etc.) inferred from examples.
5. EDGE CASES: Identify potential edge cases from constraints and example patterns.
6. RETURN TYPE: Note if examples show int, float, list, etc. — precision matters.

Format as JSON-like structure with clear section headers.""",
            context=""
        )

        # Extract function name for consistency enforcement
        func_name_match = re.search(r"Function name:\s*(\w+)", self.problem_text)
        function_name = func_name_match.group(1) if func_name_match else "unknown"

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            f"""Generate Solution Strategy 1: Direct Pattern Implementation
- Analyze examples to derive direct mathematical or logical pattern.
- Implement minimal, example-aligned solution.
- Function name MUST be: {function_name}
- Handle edge cases mentioned in decomposition: {decomposition[:500]}
- Return type must match examples exactly.""",
            
            f"""Generate Solution Strategy 2: Algorithmic Simulation
- Simulate the described process step by step (e.g., bucket lowering, element filtering).
- Prioritize clarity and correctness over optimization.
- Function name MUST be: {function_name}
- Include explicit edge case handling.
- Return type must match examples exactly.""",
            
            f"""Generate Solution Strategy 3: Library-Optimized Approach
- Use built-in Python functions or standard library for concise solution.
- Consider itertools, math, collections, etc. if appropriate.
- Function name MUST be: {function_name}
- Ensure no over-engineering — match specification exactly.
- Return type must match examples exactly."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition) for instr in strategy_instructions]
        )

        # PHASE 3: STRATEGY REFINEMENT
        refined_strategies = []
        for i, strategy in enumerate(strategies):
            refined = await self.revise(
                instruction=f"""Refine Strategy {i+1} with extreme rigor:

1. CORRECTNESS: Verify logic against ALL examples in specification.
2. EDGE CASES: Explicitly handle cases from decomposition: {decomposition[:300]}
3. TYPE SAFETY: Ensure return type matches examples (int vs float matters).
4. FUNCTION NAME: Must be exactly '{function_name}' — verify signature.
5. NO OVER-ENGINEERING: Implement ONLY what's specified.
6. ADD COMMENTS: Briefly explain key logic for maintainability.

Output ONLY the final function code with correct signature.""",
                context=strategy
            )
            refined_strategies.append(refined)

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_code = await self.ensemble(
            instruction=f"""Synthesize the best solution from candidates:

CRITERIA:
1. CORRECTNESS: Must handle all examples and inferred edge cases.
2. SIMPLICITY: Prefer minimal, readable code over complexity.
3. TYPE PRECISION: Return type must exactly match examples.
4. SIGNATURE: Function name MUST be '{function_name}'.
5. ROBUSTNESS: Should not fail on boundary conditions.

Analyze each candidate, then select or merge the optimal solution.
Output ONLY the final function code — nothing else.""",
            contexts_list=refined_strategies
        )

        # PHASE 5: VALIDATION SPIRAL (1 iteration)
        validation = await self.generate(
            instruction=f"""Act as test case designer. For function '{function_name}':

1. List 3-5 critical test cases (including edge cases) that would break a flawed implementation.
2. For each, explain expected input/output and why it's important.
3. Verify that the following code handles them correctly:

{final_code[:1000]}

If any failure is found, suggest specific fixes. Otherwise, output 'VALIDATED'.""",
            context=final_code
        )

        if "VALIDATED" not in validation and "fix" in validation.lower():
            final_code = await self.revise(
                instruction=f"""Apply critical fixes based on validation feedback:

Validation feedback: {validation[:800]}

1. Preserve function name: {function_name}
2. Maintain return type precision
3. Keep code minimal and specification-aligned
4. Output ONLY the corrected function code""",
                context=final_code
            )

        return final_code