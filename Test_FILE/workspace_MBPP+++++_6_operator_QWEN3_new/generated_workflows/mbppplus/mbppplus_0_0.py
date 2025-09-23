# Workflow ID: mbppplus_0_0
# Benchmark: mbppplus
# Data Indices: [292, 28]

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

        # Step 1: Deep problem analysis - understand intent, constraints, edge cases
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem:

            1. Problem Classification:
               - Is this a structural operation (indexing, slicing, nesting)?
               - Is this a filtering/transformation (conditionals, mappings)?
               - Is this a mathematical/computational task?
               - Does it involve string, list, set, or mixed data types?

            2. Intent Extraction:
               - What is the core operation being requested?
               - What input-output pattern is implied by the examples?
               - Are there hidden constraints not explicitly stated?

            3. Edge Case Hypothesis:
               - What edge cases might exist? (empty inputs, single elements, duplicates, type mismatches)
               - How should the function handle invalid inputs or boundary conditions?
               - Are there any implicit assumptions about data structure or order?

            4. Solution Strategy Options:
               - Propose 2-3 different approaches (imperative, functional, mathematical)
               - For each, note strengths and potential failure modes
               - Identify which approach is most likely to be robust

            5. Return Type & Structure:
               - Based on examples, what exact data type should be returned? (list, tuple, set, etc.)
               - Should order be preserved? Should duplicates be removed?

            Provide your analysis in a structured format with clear section headings.""",
            context=""
        )

        # Step 2: Conditional decomposition - only if problem is compound
        subproblems = []
        if "multiple steps" in analysis.lower() or "dependencies" in analysis.lower() or "compound" in analysis.lower():
            try:
                subproblems = await self.decompose(
                    instruction="""Break this problem into atomic subproblems:

                    - Each subproblem should be independently solvable
                    - Specify dependencies between subproblems
                    - Focus on computational steps, not just conceptual breakdown
                    - Include data flow between subproblems
                    
                    Return as list of dictionaries with 'id', 'description', 'dependencies'""",
                    context=analysis
                )
            except Exception:
                # Fallback: proceed without decomposition if it fails
                subproblems = []

        # Step 3: Parallel solution generation - explore multiple approaches
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using an IMPERATIVE approach (for loops, conditionals):

                Analysis context: {analysis}

                Requirements:
                - Use explicit loops and conditionals
                - Include defensive checks for edge cases
                - Handle empty inputs, type mismatches, and boundary conditions
                - Match return type and structure from examples
                - Add comments explaining key decisions
                - Prioritize readability and robustness over brevity""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using a FUNCTIONAL approach (list comprehensions, map/filter):

                Analysis context: {analysis}

                Requirements:
                - Use Python's functional programming features
                - Include guards for edge cases within comprehensions
                - Handle empty inputs and invalid elements gracefully
                - Match return type and structure from examples
                - Add comments explaining the functional logic
                - Prioritize elegance and conciseness while maintaining robustness""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using a MATHEMATICAL/SET-THEORETIC approach:

                Analysis context: {analysis}

                Requirements:
                - Use mathematical operations or set theory where applicable
                - Include explicit handling of edge cases
                - Handle numerical edge cases (zero, negative, overflow)
                - Match return type and structure from examples
                - Add comments explaining the mathematical insight
                - Prioritize correctness and efficiency""",
                context=analysis
            )
        )

        # Step 4: Ensemble synthesis - combine the best of all approaches
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these three approaches:

            Evaluation Criteria:
            1. Robustness: Which handles edge cases most comprehensively?
            2. Correctness: Which most precisely matches the problem requirements?
            3. Clarity: Which is easiest to understand and maintain?
            4. Efficiency: Which has the best time/space complexity?
            5. Type Safety: Which best handles type mismatches and invalid inputs?

            Synthesis Requirements:
            - Combine strengths from multiple approaches
            - Add explicit guards for: empty inputs, None values, type errors, index errors
            - Ensure return type matches examples exactly (list vs tuple vs set)
            - Preserve order if examples imply it should be preserved
            - Include comments explaining defensive programming choices
            - Prioritize correctness over brevity or elegance""",
            contexts_list=solution_approaches
        )

        # Step 5: Robustness revision - harden against edge cases
        hardened_solution = await self.revise(
            instruction="""Harden this solution against edge cases and hidden test requirements:

            Specific Requirements:
            1. Add explicit checks for:
               - Empty input lists/strings
               - Single element containers
               - Nested empty structures
               - None values
               - Type mismatches (e.g., string where number expected)
               - Index out of bounds errors
               - Division by zero or other mathematical errors

            2. Ensure return type matches examples exactly:
               - If examples return lists, return lists (not tuples or sets)
               - If order matters in examples, preserve order
               - If duplicates are preserved in examples, preserve them

            3. Add defensive programming:
               - Use try-except blocks where appropriate
               - Validate input types and structures
               - Return consistent error handling (or graceful degradation)

            4. Include comments explaining:
               - Why each edge case is handled
               - How the solution meets hidden requirements
               - Any trade-offs made for robustness

            The final solution must survive 500+ hidden edge cases.""",
            context=synthesized_solution
        )

        # Step 6: Validation - test against provided examples
        try:
            # Extract test cases from problem text if available
            test_validation = await self.programmer(
                instruction=f"""Validate this solution against the provided test cases:

                Solution to test:
                {hardened_solution}

                Instructions:
                1. Extract any assert statements from the original problem
                2. Create a test function that runs these assertions
                3. If any test fails, return the specific error and suggest a fix
                4. If all tests pass, return 'ALL TESTS PASSED'
                5. Do not modify the solution - only report results""",
                context=hardened_solution
            )
            
            # If validation fails, do one revision attempt
            if "error" in test_validation.lower() or "fail" in test_validation.lower():
                hardened_solution = await self.revise(
                    instruction=f"""Fix the solution based on these test failures:

                    Test results: {test_validation}

                    Requirements:
                    - Address the specific errors identified
                    - Maintain all previous robustness features
                    - Do not break existing functionality
                    - Keep the solution as concise as possible while fixing errors""",
                    context=hardened_solution
                )
        except Exception:
            # If validation fails catastrophically, proceed with hardened solution
            pass

        # Return final solution
        return hardened_solution