# Workflow ID: mbppplus_108_0
# Benchmark: mbppplus
# Data Indices: [277, 287]

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
        import json

        # Step 1: Classify problem type and extract constraints
        classification = await self.generate(
            instruction="""Analyze the problem and classify it into one of these categories:
            - PREDICATE: Returns boolean (True/False) based on condition evaluation
            - TRANSFORM: Returns transformed data structure (tuple, list, etc.)
            - COMPUTE: Returns scalar value (number, string, etc.)
            Also extract:
            - Expected input parameter types and structures
            - Expected return type
            - Key edge cases (empty inputs, single elements, duplicates, type mismatches)
            - Any implicit constraints or invariants
            Format as JSON with keys: "category", "input_types", "return_type", "edge_cases", "constraints"
            """,
            context=""
        )

        # Step 2: Generate synthetic test cases based on classification
        test_cases = await self.generate(
            instruction=f"""Generate 5 synthetic test cases including edge cases based on this classification:
            {classification}
            Format each test case as a Python assert statement string.
            Include at least one edge case (empty input, single element, boundary value).
            """,
            context=classification
        )

        # Step 3: Parallel solution generation with different strategies
        solution_attempts = await asyncio.gather(
            self.programmer(
                instruction=f"""Implement the function with emphasis on type safety and edge case handling.
                Classification: {classification}
                Follow return type exactly. Handle all edge cases mentioned.
                Return ONLY the function implementation with necessary imports.
                """,
                context=""
            ),
            self.programmer(
                instruction=f"""Implement the function with emphasis on algorithmic efficiency and clean logic.
                Classification: {classification}
                Prioritize readability and Pythonic style. Handle edge cases gracefully.
                Return ONLY the function implementation with necessary imports.
                """,
                context=""
            ),
            self.programmer(
                instruction=f"""Implement the function with defensive programming approach.
                Classification: {classification}
                Add explicit type checks and error handling for invalid inputs.
                Return ONLY the function implementation with necessary imports.
                """,
                context=""
            )
        )

        # Step 4: Validate and revise solutions
        validated_solutions = []
        for i, solution in enumerate(solution_attempts):
            validation = await self.generate(
                instruction=f"""Validate this solution against the problem requirements and synthetic test cases:
                Solution: {solution}
                Test Cases: {test_cases}
                Classification: {classification}
                Check for:
                - Correct return type
                - Edge case handling
                - Logical correctness
                - Type consistency
                Return "VALID" if acceptable, otherwise describe specific issues concisely.
                """,
                context=solution
            )
            
            if "VALID" not in validation.upper():
                # Revise if issues found
                revised_solution = await self.revise(
                    instruction=f"""Fix the following issues in the solution:
                    Issues: {validation}
                    Original Solution: {solution}
                    Ensure correct return type and handle all edge cases from classification: {classification}
                    Return ONLY the corrected function implementation with necessary imports.
                    """,
                    context=solution
                )
                validated_solutions.append(revised_solution)
            else:
                validated_solutions.append(solution)

        # Step 5: Ensemble final solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness (must handle all edge cases)
            - Type safety (matches expected return type)
            - Code clarity and maintainability
            - Efficiency (avoid unnecessary operations)
            Return ONLY the selected function implementation with necessary imports.
            """,
            contexts_list=validated_solutions
        )

        return final_solution