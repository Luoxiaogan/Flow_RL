# Workflow ID: mbppplus_29_0
# Benchmark: mbppplus
# Data Indices: [228, 101]

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
        import re

        # Phase 1: Strategic Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Your analysis must include:

1. Problem Classification: 
   - Is this primarily about: frequency counting, searching, sorting, mathematical computation, string manipulation, or logic validation?
   - Does it require exact computation or can it use approximations?

2. Input/Output Specification:
   - What are the exact input types and structures? (e.g., list of strings, array of integers)
   - What is the required output type and format? (e.g., single integer, string, tuple)
   - Are there any type conversion requirements?

3. Algorithmic Approach:
   - List 2-3 potential algorithmic strategies that could solve this problem
   - For each strategy, note its time/space complexity and suitability
   - Recommend the most appropriate strategy with justification

4. Edge Cases & Constraints:
   - Identify all potential edge cases (empty inputs, single elements, duplicates, boundary values)
   - Note any explicit or implicit constraints from the problem description
   - Suggest validation checks that should be included

5. Solution Modality:
   - Should this be solved via code execution, logical deduction, or mathematical proof?
   - If code is needed, specify the critical components (data structures, control flow, key operations)

Format your response as a structured analysis with clear section headers. Be thorough and precise.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        # Generate multiple solution approaches based on analysis
        solution_approaches = [
            """Implement the most straightforward, readable solution based on the recommended approach. 
            Prioritize clarity and correctness over optimization. Include comprehensive edge case handling.
            Ensure the solution matches the exact function signature and return type specified.""",
            
            """Implement an optimized solution using the most efficient algorithm identified in the analysis.
            Focus on time/space complexity improvements while maintaining correctness.
            Include comments explaining the optimization strategy.""",
            
            """Implement a defensive solution that explicitly handles all identified edge cases and constraints.
            Add validation checks and error handling even if not strictly required.
            Prioritize robustness over elegance."""
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.programmer(
                instruction=f"""Based on this problem analysis:
{problem_analysis}

{approach}

CRITICAL REQUIREMENTS:
- Use the EXACT function name and signature from the problem
- Include all necessary imports at the top of the function
- Return the exact data type specified (list vs tuple vs set matters)
- Handle ALL edge cases identified in the analysis
- Code must be self-contained (no external dependencies beyond standard library)
- Do NOT wrap in any outer function or class

Generate and execute the code to verify it works.""",
                context=problem_analysis,
                max_retries=2
            ) for approach in solution_approaches
        ]

        solutions = await asyncio.gather(*solution_tasks, return_exceptions=True)

        # Filter out any failed solutions
        valid_solutions = []
        for sol in solutions:
            if isinstance(sol, Exception):
                continue
            # Basic validation: must contain a function definition
            if 'def ' in str(sol) and 'return' in str(sol):
                valid_solutions.append(str(sol))

        if not valid_solutions:
            # Fallback: generate a simple solution
            fallback_solution = await self.programmer(
                instruction=f"""Generate a simple, correct solution based on this analysis:
{problem_analysis}

Focus on getting a working solution rather than optimization. Handle basic edge cases.
Use the exact function signature required.""",
                context=problem_analysis,
                max_retries=3
            )
            valid_solutions = [str(fallback_solution)]

        # Phase 3: Ensemble Selection
        selected_solution = await self.ensemble(
            instruction="""Evaluate these candidate solutions and select the best one based on:

1. Correctness: Does it handle all edge cases and produce correct output?
2. Robustness: Does it include appropriate validation and error handling?
3. Efficiency: Is the algorithm appropriately optimized for the problem constraints?
4. Code Quality: Is it readable, well-structured, and properly commented?
5. Specification Compliance: Does it match the required function signature and return type?

If multiple solutions are equally good, prefer the simpler, more readable one.
Return ONLY the selected solution code, nothing else.""",
            contexts_list=valid_solutions
        )

        # Phase 4: Iterative Refinement
        refined_solution = selected_solution
        for iteration in range(2):  # Maximum 2 refinement iterations
            validation_feedback = await self.generate(
                instruction=f"""Critically review this solution for the original problem:

{refined_solution}

Check for:
1. Does it match the EXACT function signature required?
2. Are all necessary imports included?
3. Does it handle ALL edge cases identified in the original analysis?
4. Is the return type correct (list vs tuple vs set)?
5. Are there any logical errors or boundary condition oversights?
6. Is the code clean, readable, and free of unnecessary complexity?

If any issues are found, provide specific, actionable revision instructions.
If no issues are found, respond with 'APPROVED'.""",
                context=refined_solution
            )

            if "APPROVED" in validation_feedback.upper():
                break

            # Revise based on feedback
            refined_solution = await self.revise(
                instruction=f"""Revise this code based on the following feedback:
{validation_feedback}

CRITICAL: Maintain the exact function signature and return type.
Fix all identified issues while preserving the core algorithm.
Ensure all edge cases are properly handled.
Return ONLY the revised code, nothing else.""",
                context=refined_solution
            )

        # Final output
        return refined_solution