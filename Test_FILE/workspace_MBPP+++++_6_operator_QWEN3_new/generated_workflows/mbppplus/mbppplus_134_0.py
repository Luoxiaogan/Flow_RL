# Workflow ID: mbppplus_134_0
# Benchmark: mbppplus
# Data Indices: [279, 205]

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

        # Step 1: Classify problem and extract core requirements
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Identify the problem category (mathematical, string manipulation, list operations, etc.)
            2. Extract input parameters and their expected types
            3. Determine exact output format and type requirements
            4. List potential edge cases (empty inputs, boundary values, type mismatches)
            5. Identify any hidden constraints or assumptions
            6. Summarize the core computational logic required
            Present your analysis in a structured, bullet-point format.""",
            context=""
        )

        # Step 2: Decompose into subproblems
        subproblems = await self.decompose(
            instruction="""Break this problem into essential subproblems with clear dependencies:
            - Input validation and type checking
            - Core algorithmic computation
            - Edge case handling
            - Output formatting and type conversion
            Each subproblem should be independently solvable and include specific success criteria.""",
            context=problem_analysis
        )

        # Step 3: Generate comprehensive test cases
        test_cases = await self.generate(
            instruction=f"""Generate comprehensive test cases for this problem including:
            - Nominal cases (typical inputs)
            - Edge cases (empty inputs, single elements, boundary values, extreme values)
            - Error cases (invalid types, null values, out-of-range values)
            - Performance cases (large inputs, repeated patterns)
            Format as Python assert statements that could be used for validation.
            Base your cases on this analysis: {problem_analysis}""",
            context=problem_analysis
        )

        # Step 4: Parallel code generation - multiple approaches
        code_candidates = await asyncio.gather(
            self.programmer(
                instruction=f"""Generate a robust Python implementation that:
                - Follows the exact function signature
                - Handles all edge cases identified in analysis
                - Returns correct data type
                - Includes defensive programming practices
                - Is clean, readable, and efficient
                Base implementation on: {problem_analysis}
                Validate against these test cases: {test_cases}""",
                context=problem_analysis,
                max_retries=3
            ),
            self.programmer(
                instruction=f"""Generate an alternative Python implementation using a different algorithmic approach:
                - If original is iterative, try recursive or functional
                - If original uses built-ins, try manual implementation
                - Focus on correctness over performance
                - Must handle same edge cases
                Base implementation on: {problem_analysis}
                Validate against these test cases: {test_cases}""",
                context=problem_analysis,
                max_retries=3
            ),
            self.programmer(
                instruction=f"""Generate a minimal, reference-style implementation similar to provided examples:
                - Simple and straightforward
                - Matches reference solution style
                - Must still handle critical edge cases
                Base implementation on: {problem_analysis}
                Validate against these test cases: {test_cases}""",
                context=problem_analysis,
                max_retries=3
            )
        )

        # Step 5: Ensemble - select or synthesize best solution
        final_code = await self.ensemble(
            instruction="""Evaluate these candidate solutions and select the best one based on:
            1. Correctness (passes all test cases)
            2. Robustness (handles edge cases gracefully)
            3. Code quality (readability, maintainability)
            4. Efficiency (appropriate for problem scale)
            5. Type safety (matches expected return type)
            If no single solution is perfect, synthesize a hybrid that combines the best elements.
            Return ONLY the final Python function implementation with imports if needed.""",
            contexts_list=code_candidates
        )

        # Step 6: Iterative refinement - validate and fix
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically review this implementation:
                {final_code}
                
                Check for:
                - Logic errors or edge case oversights
                - Type mismatches or return format issues
                - Potential runtime errors
                - Deviations from problem requirements
                If issues found, describe them specifically. If perfect, say 'VALIDATED'.""",
                context=final_code
            )
            
            if "VALIDATED" in validation or "validat" in validation.lower():
                break
                
            final_code = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                {validation}
                
                Maintain function signature and improve robustness.
                Return ONLY the corrected Python function implementation.""",
                context=final_code
            )

        # Step 7: Final formatting and type enforcement
        final_implementation = await self.revise(
            instruction="""Ensure this code meets all domain requirements:
            - EXACT function name and signature
            - Correct return type (int, str, list, tuple, etc. as required)
            - No wrapper functions or classes
            - All necessary imports included at top
            - Clean, production-ready code
            Return ONLY the final implementation - nothing else.""",
            context=final_code
        )

        return final_implementation