# Workflow ID: humaneval_63_0
# Benchmark: humaneval
# Data Indices: [96, 102]

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

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: PARALLEL DECOMPOSITION
        # Extract multiple dimensions of the problem simultaneously
        decomposition_tasks = [
            self.generate(
                instruction="""Analyze the problem specification and identify:
                1. Problem type (mathematical, string, list, logical, etc.)
                2. Key operations needed (filtering, mapping, recursion, iteration, etc.)
                3. Input/output data types and constraints
                4. Edge cases explicitly or implicitly mentioned
                5. Algorithmic patterns suggested by examples
                Provide structured analysis with clear sections.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all example input-output pairs from the docstring.
                For each example:
                - Parse the input parameters and expected output
                - Identify what the example is testing (boundary, normal case, error case)
                - Note any patterns or invariants across examples
                Format as a structured list with clear labeling.""",
                context=""
            ),
            self.generate(
                instruction="""Identify hidden constraints and assumptions:
                - What must the solution NOT do?
                - What edge cases are implied but not stated?
                - Are there performance or complexity constraints?
                - What would constitute a 'wrong' answer beyond just incorrect output?
                Think like a test case designer trying to break the solution.""",
                context=""
            )
        ]
        
        decomposition_results = await asyncio.gather(*decomposition_tasks)
        problem_analysis, examples_analysis, constraints_analysis = decomposition_results

        # PHASE 2: CONDITIONAL STRATEGY SELECTION
        # Choose generation strategy based on problem type
        strategy_analysis = await self.generate(
            instruction=f"""Based on the following analyses, select the most appropriate solution strategy:
            Problem Analysis: {problem_analysis}
            Examples: {examples_analysis}
            Constraints: {constraints_analysis}
            
            Choose from:
            A) Direct implementation (simple problems)
            B) Algorithmic pattern (mathematical/formula-based)
            C) Step-by-step procedural (complex logic)
            D) Recursive/iterative refinement (search problems)
            
            Justify your choice and outline the implementation approach.""",
            context=""
        )

        # PHASE 3: PARALLEL CANDIDATE GENERATION
        # Generate multiple solution candidates using different approaches
        candidate_instructions = [
            f"""Generate a Python function implementation based on this analysis:
            Strategy: Direct implementation
            Problem Analysis: {problem_analysis}
            Examples: {examples_analysis}
            Constraints: {constraints_analysis}
            
            Requirements:
            - Match function signature exactly
            - Handle all edge cases identified
            - Return types must match examples precisely
            - Code must be minimal and focused (no over-engineering)
            - Include comments explaining key decisions""",
            
            f"""Generate a Python function implementation based on this analysis:
            Strategy: Algorithmic pattern recognition
            Problem Analysis: {problem_analysis}
            Examples: {examples_analysis}
            Constraints: {constraints_analysis}
            
            Requirements:
            - Look for mathematical patterns or formulas in examples
            - Implement the most efficient algorithm possible
            - Handle edge cases explicitly
            - Return types must match examples precisely
            - Include comments explaining the algorithm""",
            
            f"""Generate a Python function implementation based on this analysis:
            Strategy: Step-by-step procedural approach
            Problem Analysis: {problem_analysis}
            Examples: {examples_analysis}
            Constraints: {constraints_analysis}
            
            Requirements:
            - Break problem into clear sequential steps
            - Handle each edge case explicitly
            - Return types must match examples precisely
            - Code should be readable and well-commented
            - No unnecessary abstractions"""
        ]

        candidate_tasks = [
            self.generate(instruction=instr, context="")
            for instr in candidate_instructions
        ]
        
        candidates = await asyncio.gather(*candidate_tasks)

        # PHASE 4: VALIDATION & REFINEMENT
        # Critique each candidate against the specification
        critique_tasks = [
            self.revise(
                instruction=f"""Critically evaluate this solution against the original problem specification:
                Original Analysis: {problem_analysis}
                Examples: {examples_analysis}
                Constraints: {constraints_analysis}
                
                Check for:
                1. Correct function signature and name
                2. Handling of all edge cases
                3. Return type consistency with examples
                4. Algorithmic correctness
                5. Potential off-by-one errors or boundary issues
                6. Over-engineering or unnecessary complexity
                
                If issues found, provide corrected version. If no issues, return unchanged.""",
                context=candidate
            )
            for candidate in candidates
        ]
        
        refined_candidates = await asyncio.gather(*critique_tasks)

        # PHASE 5: ENSEMBLE SYNTHESIS
        # Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below, or synthesize a new solution combining the best elements of each.
            Selection criteria:
            1. Correctness (most important)
            2. Simplicity and readability
            3. Edge case handling
            4. Adherence to specification
            5. Efficiency
            
            If synthesizing, clearly indicate which parts come from which candidate.
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=refined_candidates
        )

        # PHASE 6: FINAL VALIDATION (Optional refinement loop)
        # One final check for obvious errors
        final_check = await self.revise(
            instruction="""Final validation check:
            - Does the function name match the ENTRY POINT exactly?
            - Are all edge cases from examples handled?
            - Is the return type consistent with examples?
            - Is there any obvious logical error?
            - Is the code minimal and focused?
            
            If any issues, fix them. Otherwise, return unchanged.
            Return ONLY the Python function code.""",
            context=final_solution
        )

        return final_check