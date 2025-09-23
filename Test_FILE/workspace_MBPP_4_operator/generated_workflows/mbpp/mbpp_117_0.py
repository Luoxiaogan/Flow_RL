# Workflow ID: mbpp_117_0
# Benchmark: mbpp
# Data Indices: [63, 78]

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

        # Step 1: Extract function name and parameters
        function_info = await self.generate(
            instruction="""Extract the function name and parameters from the test cases. 
            Identify the expected input types and output format. Provide structured information.""",
            context=""
        )

        # Step 2: Generate initial code attempts
        initial_code_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the extracted information: {function_info}
                Write a Python function that satisfies the task description. Ensure proper syntax and indentation.""",
                context=function_info
            ),
            self.generate(
                instruction=f"""Using a different approach: {function_info}
                Write an alternative Python function that satisfies the task description.""",
                context=function_info
            )
        )

        # Step 3: Summarize test cases for validation
        test_cases_summary = await self.summarize(
            instruction="Condense the test cases into a concise summary for validation purposes.",
            context=self.problem_text
        )

        # Step 4: Revise code attempts based on test cases
        revised_code_attempts = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve the code to pass all test cases: {test_cases_summary}
                Address any errors or inefficiencies.""",
                context=code_attempt
            ) for code_attempt in initial_code_attempts]
        )

        # Step 5: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the most efficient, readable, and accurate solution. 
            Ensure it passes all test cases and adheres to Python best practices.""",
            contexts_list=revised_code_attempts
        )

        return final_solution