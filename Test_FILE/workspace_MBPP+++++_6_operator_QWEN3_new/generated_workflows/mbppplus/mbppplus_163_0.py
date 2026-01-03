# Workflow ID: mbppplus_163_0
# Benchmark: mbppplus
# Data Indices: [223, 310]

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

        # Phase 1: Problem Classification and Edge Case Identification
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it by:
            1. Primary operation type (filtering, mathematical computation, string manipulation, set operation, etc.)
            2. Required data structures (list, tuple, set, dictionary, etc.)
            3. Key algorithmic patterns (sorting, searching, recursion, dynamic programming, etc.)
            4. Critical edge cases (empty inputs, single elements, duplicates, negative numbers, boundary values)
            5. Expected return type and format
            6. Any potential pitfalls or common mistakes for this type of problem
            Provide a structured, detailed analysis that will guide solution generation.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the problem classification:
                {classification}
                
                Generate a Python function solution that is:
                - Correct and logically sound
                - Handles all identified edge cases
                - Efficient and clean
                - Matches the required function signature exactly
                - Uses appropriate data structures and algorithms
                - Includes comments explaining key steps
                Focus on a straightforward, readable approach.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the problem classification:
                {classification}
                
                Generate an alternative Python function solution that:
                - Uses a different algorithmic approach or data structure
                - Is optimized for performance if applicable
                - Still handles all edge cases correctly
                - Matches the required function signature
                - May be more complex but potentially more efficient
                Explain the trade-offs in your approach.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the problem classification:
                {classification}
                
                Generate a defensive Python function solution that:
                - Prioritizes robustness and edge case handling above all else
                - Includes explicit checks for invalid inputs
                - Uses clear, verbose logic that is easy to verify
                - May sacrifice some efficiency for correctness
                - Matches the required function signature
                Document all assumptions and validations.""",
                context=""
            )
        )

        # Phase 3: Parallel Solution Revision
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction="""Critically review this solution for:
                1. Logical correctness (no bugs, no skipped elements, no off-by-one errors)
                2. Complete edge case handling (test with empty, single, duplicate, boundary inputs)
                3. Efficiency (avoid unnecessary operations, use appropriate algorithms)
                4. Code clarity and maintainability
                5. Exact match to required function signature and return type
                6. Common pitfalls (e.g., modifying lists while iterating, incorrect type returns)
                Fix any issues found and return the improved solution.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Phase 4: Ensemble Selection
        best_solution = await self.ensemble(
            instruction="""Select the single best solution from the candidates based on:
            1. Correctness: Must handle all edge cases and produce correct output
            2. Robustness: Should not fail on unexpected inputs
            3. Efficiency: Prefer more efficient solutions when correctness is equal
            4. Code Quality: Clean, readable, well-commented code
            5. Avoidance of Common Pitfalls: No list modification during iteration, correct return types, etc.
            Justify your selection with a brief rationale.""",
            contexts_list=revised_solutions
        )

        # Phase 5: Generate Final Executable Code
        final_code = await self.programmer(
            instruction=f"""Generate the final Python function implementation based on this selected solution:
            {best_solution}
            
            Requirements:
            - Use the EXACT function name and parameters from the original problem
            - Include all necessary imports at the top
            - Return the correct data type (list, tuple, int, etc.) as specified
            - Handle all edge cases identified in the classification
            - Be efficient and clean
            - Do NOT include any test cases or print statements
            - Return ONLY the function implementation as specified in the output format
            
            Ensure the code is production-ready and will pass rigorous testing.""",
            context=best_solution,
            max_retries=3
        )

        return final_code