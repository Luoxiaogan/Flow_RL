# Workflow ID: mbpp_35_0
# Benchmark: mbpp
# Data Indices: [27]

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

        # Step 1: Initial Analysis
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the test cases.
            Look for patterns like 'assert function_name(args)'.
            Return ONLY the function name without any additional text.""",
            context=""
        )

        task_interpretation = await self.generate(
            instruction=f"""Interpret the task description:
            Function Name: {function_name_extraction}
            Task Description: [Original Problem]
            Identify the main requirements, input/output types, and any implicit constraints.""",
            context=""
        )

        # Step 2: Parallel Exploration
        solution_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Propose a solution using string manipulation methods:
                Task Interpretation: {task_interpretation}""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a solution using regular expressions:
                Task Interpretation: {task_interpretation}""",
                context=""
            )
        )

        edge_cases = await self.generate(
            instruction=f"""Identify potential edge cases:
            Task Interpretation: {task_interpretation}
            Consider inputs like empty strings, strings with only spaces, etc.""",
            context=""
        )

        # Step 3: Synthesis
        synthesized_solution = await self.ensemble(
            instruction=f"""Combine the following solution strategies into a unified approach:
            Strategy 1: {solution_strategies[0]}
            Strategy 2: {solution_strategies[1]}
            Edge Cases: {edge_cases}""",
            contexts_list=solution_strategies + [edge_cases]
        )

        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the synthesized solution:
            Function Name: {function_name_extraction}
            Solution: {synthesized_solution}""",
            context=""
        )

        # Step 4: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the following code against the test cases and edge cases:
            Code: {initial_code}
            Test Cases: [Original Problem TEST CASES]
            Edge Cases: {edge_cases}""",
            context=initial_code
        )

        refined_code = await self.revise(
            instruction=f"""Refine the code based on validation results:
            Validation Results: {validation}
            Original Code: {initial_code}""",
            context=initial_code
        )

        # Step 5: Final Output
        final_code = await self.revise(
            instruction="""Ensure the code is complete, executable, and adheres to Python conventions:
            - Include all necessary imports at the top
            - Use 4-space indentation
            - Ensure the function name matches the test cases""",
            context=refined_code
        )

        return final_code