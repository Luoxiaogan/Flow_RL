# Workflow ID: humaneval_51_0
# Benchmark: humaneval
# Data Indices: [82, 123]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: STRUCTURED PROBLEM ANALYSIS
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this code generation problem. Extract and organize:

1. FUNCTION CONTRACT:
   - Exact function name (ENTRY POINT) that must be used
   - Expected input types and output types (infer from examples)
   - Any explicit constraints mentioned

2. EXAMPLE DECONSTRUCTION:
   - For each example in docstring, write input → expected output
   - Identify patterns or formulas connecting input to output
   - Note any discrepancies or special cases

3. EDGE CASE IDENTIFICATION:
   - What boundary conditions are implied? (empty input, single element, zero, negative, etc.)
   - What would break a naive implementation?

4. IMPLEMENTATION STRATEGY OPTIONS:
   - List 2-3 different approaches to solve this (e.g., direct simulation, mathematical formula, iterative filtering)
   - For each, note pros/cons and which examples it handles best

Format as clearly labeled sections. Be exhaustive — hidden test cases will target your blind spots.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION HYPOTHESIS GENERATION
        # Three distinct approaches generated in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code implementing the function exactly as specified.
APPROACH: Literal Interpretation
- Directly translate docstring examples into code logic
- Prioritize clarity and direct mapping over optimization
- Handle examples first, then generalize
- MUST use exact function name from ENTRY POINT
- Return type must match examples precisely (int/float/bool/list)
Context from analysis: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code implementing the function exactly as specified.
APPROACH: Edge-Case First
- Start by handling all edge cases identified in analysis
- Build core logic only after edge cases are covered
- Use defensive programming: check boundaries early
- MUST use exact function name from ENTRY POINT
- Return type must match examples precisely
Context from analysis: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code implementing the function exactly as specified.
APPROACH: Algorithmic Generalization
- Derive mathematical pattern or algorithm from examples
- Implement general solution, then verify against examples
- Optimize for correctness over readability
- MUST use exact function name from ENTRY POINT
- Return type must match examples precisely
Context from analysis: {problem_analysis}""",
                context=problem_analysis
            )
        )

        # PHASE 3: PARALLEL SELF-CRITIQUE & VALIDATION
        # Each solution is revised by simulating example execution
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically revise this code by simulating execution against ALL docstring examples:

1. For each example in the original problem:
   - Trace through code step by step
   - Verify output matches expected result
   - Check return type matches exactly (int vs float matters)

2. Verify edge cases from analysis are handled:
   {problem_analysis}

3. Fix any mismatches, type errors, or logic flaws

4. Ensure:
   - Function name matches ENTRY POINT exactly
   - No extra imports or over-engineering
   - Code is minimal but correct

Return only the corrected code, nothing else.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_code = await self.ensemble(
            instruction=f"""Synthesize the best possible solution from these candidates:

1. EVALUATE each solution against:
   - Correctness on all docstring examples (simulate execution)
   - Handling of edge cases identified in analysis
   - Type consistency with examples
   - Code simplicity and directness

2. COMBINE strengths:
   - Take correct logic from one, edge handling from another
   - Resolve conflicts by preferring solutions that handle more cases

3. OUTPUT REQUIREMENTS:
   - Must be valid Python code with exact function name
   - Must return correct type for all examples
   - Must handle all edge cases
   - Remove any unnecessary complexity

4. If all solutions have flaws, create a new synthesis that fixes them.

Return only the final code, nothing else.

Problem Analysis for context: {problem_analysis}""",
            contexts_list=validated_solutions
        )

        # PHASE 5: FINAL POLISH & CONTRACT VERIFICATION
        polished_code = await self.revise(
            instruction="""Final verification and polish:

1. CHECK FUNCTION NAME:
   - Must match ENTRY POINT exactly (case-sensitive)
   - No typos or variations

2. CHECK RETURN TYPES:
   - Must match examples precisely (int vs float vs bool)
   - No unnecessary type conversions

3. REMOVE ANY:
   - Extra imports
   - Debug prints
   - Comments not in original spec
   - Over-engineered logic

4. ENSURE:
   - Code is minimal and direct
   - Implements exactly what's specified, nothing more

Return only the cleaned code, nothing else.""",
            context=final_code
        )

        return polished_code