# Workflow ID: mbppplus_180_0
# Benchmark: mbppplus
# Data Indices: [366, 31]

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

        # PHASE 1: Problem Decomposition & Constraint Extraction
        decomposition_instruction = """
        Systematically decompose this programming problem into its core components:
        1. Identify the INPUT data structure(s) and their constraints (e.g., list of integers, string with mixed case)
        2. Identify the OUTPUT data structure and format requirements (e.g., must return tuple, preserve order)
        3. Extract functional requirements: what transformation or computation must occur?
        4. Infer implicit constraints from test cases and problem context (e.g., handle empty input, no external libraries)
        5. List all edge cases that must be handled (empty input, single element, duplicates, boundary values)
        6. Determine if order preservation is required
        7. Identify any performance or complexity constraints
        Present as a structured markdown report with clear sections.
        """
        decomposition = await self.generate(instruction=decomposition_instruction, context="")

        # PHASE 2: Parallel Strategy Generation
        strategy_instructions = [
            """
            Generate a solution using IMPERATIVE programming style:
            - Use explicit loops and conditionals
            - Focus on readability and step-by-step logic
            - Include detailed comments explaining each step
            - Handle all edge cases identified in decomposition
            """,
            """
            Generate a solution using FUNCTIONAL programming style:
            - Use list comprehensions, filter, map, reduce where appropriate
            - Avoid explicit loops
            - Focus on declarative transformations
            - Include type annotations and docstring
            """,
            """
            Generate a solution using MATHEMATICAL/SET-THEORETIC approach:
            - Look for underlying mathematical patterns or set operations
            - Optimize for efficiency (time/space complexity)
            - Use built-in functions and data structures creatively
            - Include complexity analysis in comments
            """
        ]

        # Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(instruction=instr + f"\n\nBASED ON DECOMPOSITION:\n{decomposition}", context="")
            for instr in strategy_instructions
        ]
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Adversarial Validation & Refinement
        refined_strategies = []
        for i, strategy in enumerate(raw_strategies):
            validation_instruction = f"""
            CRITICALLY REVISE this solution strategy (Strategy {i+1}):

            1. Verify it handles ALL edge cases from decomposition: {decomposition}
            2. Check type consistency (input/output types match requirements)
            3. Ensure no mutation of input parameters unless explicitly allowed
            4. Validate against performance constraints if any
            5. Fix any logical errors or boundary condition oversights
            6. Improve code clarity and add defensive programming checks
            7. Ensure return type exactly matches expected format (list vs tuple vs set)

            Return the corrected, production-ready version with comprehensive error handling.
            """
            refined = await self.revise(instruction=validation_instruction, context=strategy)
            refined_strategies.append(refined)

        # PHASE 4: Ensemble Synthesis
        synthesis_instruction = f"""
        SYNTHESIZE the best elements from all refined strategies into one optimal solution:

        Consider:
        - Which approach handles edge cases most robustly?
        - Which has the clearest, most maintainable code?
        - Which best meets performance requirements?
        - Which most precisely matches output format requirements?

        Create a hybrid solution that:
        1. Uses the most reliable edge-case handling from any strategy
        2. Adopts the clearest code structure
        3. Maintains required performance characteristics
        4. Exactly matches expected return type and format
        5. Includes comprehensive comments and type hints

        Prioritize correctness and robustness over cleverness.
        """
        synthesized_solution = await self.ensemble(
            instruction=synthesis_instruction,
            contexts_list=refined_strategies
        )

        # PHASE 5: Code Verification & Iterative Refinement
        max_attempts = 3
        final_solution = synthesized_solution
        test_results = None

        for attempt in range(max_attempts):
            # Generate comprehensive test cases based on decomposition
            test_case_instruction = f"""
            Generate a comprehensive test suite based on problem decomposition:
            {decomposition}

            Include:
            - Basic functionality tests
            - All identified edge cases
            - Type consistency tests
            - Performance boundary tests if applicable
            - Format validation tests (list vs tuple vs set)

            Format as Python assert statements only.
            """
            test_cases = await self.generate(instruction=test_case_instruction, context=decomposition)

            # Execute solution against test cases
            verification_instruction = f"""
            Execute the following solution against the provided test cases.
            If any test fails, return detailed error messages.
            If all pass, return "SUCCESS".

            SOLUTION TO TEST:
            {final_solution}

            TEST CASES:
            {test_cases}
            """
            test_results = await self.programmer(instruction=verification_instruction, context="")

            if "SUCCESS" in test_results.upper() and "ERROR" not in test_results.upper():
                break
            else:
                # Refine based on test failures
                refinement_instruction = f"""
                The solution failed testing with these errors:
                {test_results}

                Revise the solution to fix ALL identified issues:
                1. Address specific test failures mentioned
                2. Strengthen edge case handling
                3. Verify type consistency
                4. Ensure output format matches exactly

                Return the corrected implementation.
                """
                final_solution = await self.revise(instruction=refinement_instruction, context=final_solution)
        else:
            # If all attempts fail, return best effort with warning
            final_solution = "# WARNING: Solution may not pass all tests\n" + final_solution

        # Extract just the function code (remove any markdown or explanations)
        code_extraction_instruction = """
        Extract ONLY the Python function implementation from the text below.
        Remove any markdown code fences, explanations, or additional text.
        Return ONLY the raw Python code that defines the function.
        Preserve all imports, function signature, and docstrings if present.
        """
        clean_code = await self.generate(instruction=code_extraction_instruction, context=final_solution)

        return clean_code