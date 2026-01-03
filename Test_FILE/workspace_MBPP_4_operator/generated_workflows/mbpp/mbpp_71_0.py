# Workflow ID: mbpp_71_0
# Benchmark: mbpp
# Data Indices: [254]

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

        # Step 1: Initial Analysis - Extract function name and requirements
        analysis = await self.generate(
            instruction="""Extract the following information from the problem text and test cases:
            1. Function name (from assert statements)
            2. Input types and expected output types
            3. Key requirements and constraints
            Provide this information in a structured format.""",
            context=""
        )

        # Parse function name and requirements
        func_name_match = re.search(r"assert\s+(\w+)\(", analysis)
        func_name = func_name_match.group(1) if func_name_match else "unknown_function"
        requirements = analysis.split("Key requirements and constraints:")[-1].strip()

        # Step 2: Parallel Exploration of Solution Strategies
        std_lib_solution = await self.generate(
            instruction=f"""Using Python's standard library, implement a solution for the following:
            Function Name: {func_name}
            Requirements: {requirements}
            Focus on leveraging built-in functions and modules.""",
            context=analysis
        )

        custom_algo_solution = await self.generate(
            instruction=f"""Implement a custom algorithm for the following:
            Function Name: {func_name}
            Requirements: {requirements}
            Avoid using standard library functions unless absolutely necessary.""",
            context=analysis
        )

        # Step 3: Ensemble to Select Best Solution
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on the following criteria:
            1. Correctness (passes all test cases)
            2. Simplicity (easier to understand and maintain)
            3. Efficiency (minimizes computational overhead)
            Compare these solutions:
            - Standard Library Solution: {std_lib_solution}
            - Custom Algorithm Solution: {custom_algo_solution}""",
            contexts_list=[std_lib_solution, custom_algo_solution]
        )

        # Step 4: Code Validation and Iterative Refinement
        code_valid = False
        refined_code = best_solution
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the following code against the test cases:
                Code: {refined_code}
                Test Cases: {self.problem_text}
                Identify any errors or inefficiencies.""",
                context=refined_code
            )
            if "error" not in validation.lower():
                code_valid = True
                break
            refined_code = await self.revise(
                instruction=f"""Fix the following issues in the code:
                Issues: {validation}
                Original Code: {refined_code}""",
                context=refined_code
            )

        # Step 5: Final Output Formatting
        final_code = f"""