# Workflow ID: mbpp_58_0
# Benchmark: mbpp
# Data Indices: [354, 352]

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

        # Initial analysis to extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify the task description.
            - Extract the function name from the test cases.
            - Infer input/output types and potential edge cases.
            Provide structured findings.""",
            context=""
        )

        # Parse function name and test cases
        function_info = await self.generate(
            instruction=f"""From the following analysis:
            {initial_analysis}
            
            Isolate the function name and summarize the expected behavior.
            Ensure the function name matches the test cases exactly.""",
            context=initial_analysis
        )

        # Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Directly translate the task description into Python code:
                Task: {initial_analysis}
                Function: {function_info}""",
                context=""
            ),
            self.generate(
                instruction=f"""Focus on mathematical or algorithmic approaches:
                Task: {initial_analysis}
                Function: {function_info}""",
                context=""
            ),
            self.generate(
                instruction=f"""Explicitly handle edge cases:
                Task: {initial_analysis}
                Function: {function_info}""",
                context=""
            )
        )

        # Refine each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the following solution:
                - Address ambiguities.
                - Improve clarity and correctness.
                - Ensure proper imports and indentation.
                Solution: {strategy}""",
                context=strategy
            ) for strategy in strategies]
        )

        # Ensemble selection to choose the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate and select the best solution:
            Criteria:
            - Passes all test cases.
            - Handles edge cases effectively.
            - Code is clean, readable, and efficient.""",
            contexts_list=refined_strategies
        )

        return final_solution