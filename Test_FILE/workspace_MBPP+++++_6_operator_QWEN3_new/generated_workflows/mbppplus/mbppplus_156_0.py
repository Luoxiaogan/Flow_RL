# Workflow ID: mbppplus_156_0
# Benchmark: mbppplus
# Data Indices: [86, 212]

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

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into essential components:
            1. Identify input parameters: their types, expected formats, and possible variations
            2. Determine expected output: exact type, format, and examples from test cases
            3. Extract edge cases: empty inputs, single elements, boundary values, special conditions
            4. Identify algorithmic patterns: what kind of computation or transformation is needed?
            5. Note any constraints: time complexity, space complexity, or specific implementation requirements
            Return each component as a separate subproblem with clear descriptions.""",
            context=""
        )

        # Convert decomposition to readable context
        decomposition_context = "\n".join([
            f"Component {i+1}: {item['description']}" 
            for i, item in enumerate(decomposition)
        ])

        # Step 2: Parallel generation of solution approaches
        direct_solution, optimized_solution, defensive_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct, straightforward implementation:
                - Focus on clarity and simplicity
                - Implement exactly what's asked without over-engineering
                - Use the function signature provided
                - Include basic edge case handling
                Problem context: {decomposition_context}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an optimized, efficient implementation:
                - Focus on algorithmic efficiency and clean code
                - Consider time/space complexity improvements
                - Handle all edge cases identified in decomposition
                - Maintain readability while optimizing
                Problem context: {decomposition_context}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a defensive, robust implementation:
                - Include comprehensive error handling and input validation
                - Explicitly handle all edge cases from decomposition
                - Add type checking and boundary condition verification
                - Prioritize correctness over elegance
                Problem context: {decomposition_context}""",
                context=""
            )
        )

        # Step 3: Revise each solution for quality improvement
        revised_solutions = await asyncio.gather(
            self.revise(
                instruction="""Improve this solution:
                - Fix any logical errors or edge case oversights
                - Ensure type consistency with expected output
                - Improve code clarity and documentation
                - Verify function signature matches exactly""",
                context=direct_solution
            ),
            self.revise(
                instruction="""Optimize and refine this solution:
                - Ensure algorithmic efficiency is maintained
                - Add comments explaining complex logic
                - Verify all edge cases are properly handled
                - Confirm return type matches requirements""",
                context=optimized_solution
            ),
            self.revise(
                instruction="""Strengthen this defensive solution:
                - Add more comprehensive error messages
                - Verify input validation covers all cases
                - Ensure robust handling of unexpected inputs
                - Maintain type safety throughout""",
                context=defensive_solution
            )
        )

        # Step 4: Ensemble synthesis - combine the best elements
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best elements from all three solutions:
            1. Take the clarity and simplicity from the direct solution
            2. Incorporate the efficiency and optimization from the optimized solution
            3. Integrate the robustness and error handling from the defensive solution
            4. Ensure the final code:
               - Uses the exact function signature specified
               - Returns the correct data type (list, tuple, set, etc.)
               - Handles all identified edge cases
               - Is clean, readable, and well-commented
            5. Remove any redundant or conflicting code
            6. Present only the final function implementation with necessary imports
            Problem context: {decomposition_context}""",
            contexts_list=list(revised_solutions)
        )

        # Step 5: Validation loop - test and refine if needed
        for attempt in range(3):
            try:
                # Extract test cases from problem text if available
                test_cases_match = re.search(r'BASIC TEST CASES:\s*