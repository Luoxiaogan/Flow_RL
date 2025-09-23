# Workflow ID: mbpp_67_0
# Benchmark: mbpp
# Data Indices: [324, 326]

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

        # Step 1: Extract function name and input/output patterns from test cases
        function_analysis = await self.generate(
            instruction="""Extract the function name and input/output patterns from the test cases.
            - Identify the function name used in the assert statements.
            - Determine the types of inputs (e.g., tuple, list, tree) and outputs (e.g., integer, string).
            - Provide a structured summary of the findings.""",
            context=""
        )

        # Step 2: Interpret the task description
        task_interpretation = await self.generate(
            instruction=f"""Interpret the natural language task description.
            - Break down the task into inputs, outputs, and operations.
            - Infer any missing constraints or edge cases.
            - Use the following function analysis as context: {function_analysis}""",
            context=function_analysis
        )

        # Step 3: Generate multiple solution drafts
        drafts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate an iterative solution for the task.
                - Use the following task interpretation: {task_interpretation}
                - Ensure the solution aligns with the function name and input/output patterns.""",
                context=task_interpretation
            ),
            self.generate(
                instruction=f"""Generate a recursive solution for the task.
                - Use the following task interpretation: {task_interpretation}
                - Ensure the solution aligns with the function name and input/output patterns.""",
                context=task_interpretation
            )
        )

        # Step 4: Validate and refine each draft
        refined_drafts = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine the following code:
                - Check for correctness, efficiency, and readability.
                - Address any edge cases or missing details.
                - Ensure proper syntax and formatting.""",
                context=draft
            ) for draft in drafts]
        )

        # Step 5: Select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on the following criteria:
            - Correctness: Does it pass all test cases?
            - Efficiency: Is it computationally optimal?
            - Readability: Is the code clean and well-documented?""",
            contexts_list=refined_drafts
        )

        # Step 6: Verify completeness and executability
        verified_code = await self.summarize(
            instruction=f"""Verify that the final solution is complete and executable:
            - Include all necessary imports at the top.
            - Ensure proper indentation and formatting.
            - Confirm the function name matches the test cases exactly.
            Final solution: {final_solution}""",
            context=final_solution
        )

        return verified_code