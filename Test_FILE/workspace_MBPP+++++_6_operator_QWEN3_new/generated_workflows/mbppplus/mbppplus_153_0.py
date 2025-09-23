# Workflow ID: mbppplus_153_0
# Benchmark: mbppplus
# Data Indices: [121, 2]

import asyncio

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
        import json

        # Phase 1: Problem Classification & Semantic Analysis
        classification = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem. Answer:
            1. Primary operation type: filtering, transformation, sequence generation, search, sort, or other?
            2. Data structures involved: list, dict, tuple, set, string, or mixed?
            3. Key constraints: boundary conditions, edge cases, type requirements?
            4. Algorithmic pattern: iterative, recursive, sieve, two-pointer, etc.?
            5. Expected output format: exact data type and structure?
            Format as JSON with keys: operation_type, data_structures, constraints, algorithmic_pattern, output_format.""",
            context=""
        )

        # Phase 2: Decompose into Subproblems
        subproblems = await self.decompose(
            instruction="""Break this problem into minimal, independent subproblems. For each:
            - What atomic operation must be performed?
            - What are its input/output specifications?
            - What edge cases must it handle?
            - Does it depend on other subproblems?
            Prioritize subproblems that handle edge cases and type validation first.""",
            context=classification
        )

        # Phase 3: Parallel Solution Generation & Validation
        solution_attempts = []
        validation_tasks = []

        # Generate multiple solution approaches in parallel
        for i, approach in enumerate(["direct_implementation", "defensive_programming", "algorithm_optimized"]):
            attempt = await self.generate(
                instruction=f"""Generate a Python function solution using {approach} strategy. 
                Consider: {classification}
                Subproblems to address: {[sp['description'] for sp in subproblems]}
                Requirements:
                - Match exact function signature from problem
                - Handle all edge cases identified
                - Include necessary imports inside function
                - Return correct data type
                - No wrapper code or explanations — only function definition""",
                context=""
            )
            solution_attempts.append(attempt)

        # Parallel validation streams
        for solution in solution_attempts:
            validation_tasks.append(self.generate(
                instruction=f"""Critically validate this solution:
                1. Does it handle empty inputs?
                2. Does it preserve required data types?
                3. Are boundary conditions correctly managed?
                4. Is the algorithm logically sound?
                5. Any off-by-one or indexing errors?
                Return 'PASSED' if flawless, otherwise detailed error description.""",
                context=solution
            ))

        validation_results = await asyncio.gather(*validation_tasks)

        # Phase 4: Ensemble Selection & Refinement
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness (passed validation)
            - Code clarity
            - Edge case coverage
            - Efficiency
            If multiple passed, choose most readable. If none passed, select least flawed for revision.""",
            contexts_list=solution_attempts
        )

        # Phase 5: Iterative Refinement Loop
        current_solution = best_solution
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Final validation pass:
                - Check function signature matches exactly
                - Verify imports are inside function
                - Confirm no extra text or markdown
                - Test with edge cases: empty input, single element, duplicates
                Return 'VALID' if perfect, otherwise specific fixes needed.""",
                context=current_solution
            )
            
            if "VALID" in validation or "PASSED" in validation:
                break
                
            # Revise based on feedback
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                Validation feedback: {validation}
                Requirements:
                - Maintain exact function signature
                - Keep imports inside function
                - Output ONLY function definition, no explanations
                - Address all edge cases mentioned""",
                context=current_solution
            )

        # Phase 6: Format Enforcement & Final Output
        final_output = await self.revise(
            instruction="""Ensure output is EXACTLY:
            - Only the function implementation
            - Correct function name and parameters
            - All imports inside function body
            - No extra text, markdown, or explanations
            - Proper indentation and syntax
            If any deviation, correct it immediately.""",
            context=current_solution
        )

        return final_output