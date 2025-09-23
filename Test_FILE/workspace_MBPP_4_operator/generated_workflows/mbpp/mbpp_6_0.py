# Workflow ID: mbpp_6_0
# Benchmark: mbpp
# Data Indices: [360]

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

        # Step 1: Extract function name and analyze task description
        analysis = await self.generate(
            instruction="""Extract the function name from the test cases and analyze the task description:
            - Identify the function name and its arguments.
            - Summarize the task requirements.
            - Highlight any ambiguities or missing details.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a solution using a procedural approach:
                - Break the problem into sequential steps.
                - Ensure all requirements are addressed.
                Analysis: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a solution using a functional programming approach:
                - Use higher-order functions like map, filter, and reduce.
                - Focus on immutability and pure functions.
                Analysis: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a solution using Python's standard library:
                - Leverage built-in modules like itertools, collections, or re.
                - Optimize for readability and efficiency.
                Analysis: {analysis}""",
                context=""
            )
        )

        # Step 3: Validate and refine solutions
        validated_solutions = []
        for strategy in strategies:
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                - Check if all assertions pass.
                - Identify any errors or inconsistencies.
                Solution: {strategy}""",
                context=analysis
            )
            if "error" not in validation.lower():
                validated_solutions.append(strategy)
            else:
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    - Fix identified issues.
                    - Improve clarity and correctness.
                    Feedback: {validation}
                    Solution: {strategy}""",
                    context=strategy
                )
                validated_solutions.append(refined)

        # Step 4: Select the best solution
        best_solution = await self.ensemble(
            instruction="""Select the most robust and efficient solution:
            - Consider correctness, readability, and performance.
            - Favor solutions that pass all test cases and handle edge cases.""",
            contexts_list=validated_solutions
        )

        return best_solution