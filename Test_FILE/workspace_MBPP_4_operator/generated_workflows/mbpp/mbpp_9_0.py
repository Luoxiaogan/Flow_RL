# Workflow ID: mbpp_9_0
# Benchmark: mbpp
# Data Indices: [214]

import asyncio
import re

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
        import re

        # --- Initial Analysis ---
        # Extract function name using regex
        function_name_match = re.search(r'assert\s+(\w+)\(', self.problem_text)
        if function_name_match:
            function_name = function_name_match.group(1)
        else:
            raise ValueError("Function name not found in test cases")

        # Break down task description
        initial_analysis = await self.generate(
            instruction="""Analyze the task description:
            - Identify key operations (e.g., sorting, mathematical computations)
            - Note any constraints or special conditions
            - Determine input and output types""",
            context=""
        )

        # --- Parallel Exploration ---
        # Generate multiple solution attempts
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on list/array operations:
                Function name: {function_name}
                Task details: {initial_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on mathematical computations:
                Function name: {function_name}
                Task details: {initial_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on string manipulation:
                Function name: {function_name}
                Task details: {initial_analysis}""",
                context=""
            )
        )

        # --- Synthesis ---
        # Select the best solution
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on:
            - Alignment with test cases
            - Adherence to Pythonic practices
            - Completeness and clarity""",
            contexts_list=solutions
        )

        # --- Validation and Refinement ---
        # Validate the selected solution
        validation = await self.generate(
            instruction=f"""Validate the solution against test cases:
            Solution: {best_solution}
            Test cases: {self.problem_text}""",
            context=""
        )

        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                Feedback: {validation}
                Original solution: {best_solution}""",
                context=best_solution
            )
            best_solution = refined_solution

        # --- Final Output ---
        # Ensure the final code includes all necessary imports and is properly formatted
        final_code = f"""