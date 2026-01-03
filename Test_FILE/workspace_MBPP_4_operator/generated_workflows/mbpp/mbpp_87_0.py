# Workflow ID: mbpp_87_0
# Benchmark: mbpp
# Data Indices: [108]

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

        # Step 1: Extract function name from assert statements
        function_name = await self.generate(
            instruction="""Extract the function name from the assert statements in the test cases. 
            The function name appears before the parentheses in the assert statements. 
            Return ONLY the function name without any additional text.""",
            context=""
        )

        # Step 2: Analyze the problem description
        problem_analysis = await self.generate(
            instruction=f"""Analyze the problem description and classify it into one of the following categories:
            - List/Array Operations
            - Mathematical Computations
            - String Manipulation
            - Data Structures
            - Standard Library Usage
            
            Based on the classification, identify:
            - Input types and formats
            - Expected output types and formats
            - Key operations or transformations required
            - Any constraints or edge cases mentioned
            
            Problem Description: {self.problem_text}""",
            context=""
        )

        # Step 3: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Generate Python code to solve the problem. 
            Use the function name: {function_name}.
            Problem Analysis: {problem_analysis}
            Ensure the code includes:
            - Proper function signature
            - Necessary imports
            - Correct logic to handle the problem requirements
            - Comments explaining key steps""",
            context=""
        )

        # Step 4: Validate and refine solution
        MAX_ITERATIONS = 3
        solution = initial_solution
        for i in range(MAX_ITERATIONS):
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases.
                Solution: {solution}
                Test Cases: {self.problem_text}
                Identify any errors or mismatches and describe them.""",
                context=""
            )

            if "error" not in validation.lower():
                break  # Solution is valid

            solution = await self.revise(
                instruction=f"""Refine the solution based on the following feedback:
                Feedback: {validation}
                Original Solution: {solution}
                Ensure the refined solution addresses all issues and passes the test cases.""",
                context=solution
            )

        # Step 5: Optional parallel exploration for complex problems
        if "complex" in problem_analysis.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Generate alternative solution using a different approach...", context=""),
                self.generate(instruction="Generate alternative solution focusing on efficiency...", context="")
            )
            solution = await self.ensemble(
                instruction="Select the best solution based on correctness, clarity, and efficiency.",
                contexts_list=candidates
            )

        # Step 6: Format final output
        final_output = f"