# Workflow ID: mbpp_64_0
# Benchmark: mbpp
# Data Indices: [85, 128]

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

        # Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract key components from the problem:
            - Task description
            - Input types and formats
            - Output types and formats
            - Function name from assert statements
            Provide structured information.""",
            context=""
        )

        # Parallel Exploration
        exploration_tasks = [
            self.generate(
                instruction=f"""Generate a solution using built-in functions:
                {initial_analysis}
                Ensure proper imports and function name usage.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using custom algorithms:
                {initial_analysis}
                Focus on clarity and correctness.""",
                context=initial_analysis
            )
        ]
        explorations = await asyncio.gather(*exploration_tasks)

        # Solution Synthesis
        synthesis = await self.ensemble(
            instruction="""Select or synthesize the best solution:
            - Ensure all test cases are satisfied
            - Handle edge cases
            - Maintain code readability""",
            contexts_list=explorations
        )

        # Iterative Refinement
        refined_solution = synthesis
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                Check for:
                - Syntax errors
                - Logical errors
                - Missing edge case handling""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Fix issues identified during validation:
                    {validation}
                    Improve code quality and robustness.""",
                    context=refined_solution
                )
            else:
                break

        # Final Output
        final_code = await self.summarize(
            instruction="""Condense the final solution into a clean, executable format:
            - Include all necessary imports
            - Ensure proper indentation
            - Match function name from test cases""",
            context=refined_solution
        )

        return final_code