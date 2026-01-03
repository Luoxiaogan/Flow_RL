# Workflow ID: mbpp_11_0
# Benchmark: mbpp
# Data Indices: [243]

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

        # Step 1: Extract function name and analyze problem
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and analyze the problem:
            - Identify the function name used in the assert statements.
            - Parse the natural language description to determine the task requirements.
            - Identify input types, operations, and constraints.
            Provide structured output.""",
            context=""
        )

        # Extract function name using regex
        function_name_match = re.search(r"assert\s+(\w+)\(", self.problem_text)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Step 2: Generate multiple solution candidates
        direct_translation = await self.generate(
            instruction=f"""Generate a direct translation of the problem into Python code:
            Function name: {function_name}
            Task requirements: {analysis}
            Ensure proper syntax, indentation, and imports.""",
            context=analysis
        )

        standard_library = await self.generate(
            instruction=f"""Generate a solution leveraging Python's standard library:
            Function name: {function_name}
            Task requirements: {analysis}
            Use built-in functions and modules like itertools, math, etc.""",
            context=analysis
        )

        algorithmic_approach = await self.generate(
            instruction=f"""Generate an algorithmic solution:
            Function name: {function_name}
            Task requirements: {analysis}
            Focus on clear logic and efficiency.""",
            context=analysis
        )

        # Step 3: Ensemble selection
        selected_solution = await self.ensemble(
            instruction=f"""Select the best solution based on:
            - Clarity and readability
            - Correctness and alignment with task requirements
            - Efficiency and use of Python features
            Candidates:
            1. Direct Translation: {direct_translation}
            2. Standard Library: {standard_library}
            3. Algorithmic Approach: {algorithmic_approach}""",
            contexts_list=[direct_translation, standard_library, algorithmic_approach]
        )

        # Step 4: Validate and refine
        max_iterations = 3
        for _ in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                Function name: {function_name}
                Solution: {selected_solution}
                Identify any errors or mismatches.""",
                context=selected_solution
            )

            if "error" not in validation.lower():
                break  # Solution is valid

            # Refine the solution
            selected_solution = await self.revise(
                instruction=f"""Revise the solution to fix errors:
                Errors: {validation}
                Original solution: {selected_solution}""",
                context=selected_solution
            )

        # Step 5: Final output
        return f"""