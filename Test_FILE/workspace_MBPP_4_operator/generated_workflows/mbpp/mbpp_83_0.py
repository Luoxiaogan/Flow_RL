# Workflow ID: mbpp_83_0
# Benchmark: mbpp
# Data Indices: [83, 261]

import asyncio

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

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract key information from the problem:
            - Function name from test cases
            - Inputs, outputs, and their types
            - Constraints and requirements
            - Problem classification (e.g., list operations, string manipulations)""",
            context=""
        )

        # Extract function name using regex
        function_name_match = re.search(r'assert\s+(\w+)\(', self.problem_text)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Phase 2: Solution Exploration
        direct_translation, pattern_matching, library_utilization = await asyncio.gather(
            self.generate(
                instruction=f"""Directly translate the problem description into Python code:
                Function name: {function_name}
                Requirements: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Identify common programming patterns and map them to Python constructs:
                Function name: {function_name}
                Requirements: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Utilize Python standard library functions to solve the problem:
                Function name: {function_name}
                Requirements: {analysis}""",
                context=""
            )
        )

        # Phase 3: Synthesis and Validation
        best_solution = await self.ensemble(
            instruction=f"""Select the most promising solution based on:
            - Clarity and readability
            - Correctness and adherence to requirements
            - Efficiency and simplicity""",
            contexts_list=[direct_translation, pattern_matching, library_utilization]
        )

        validation = await self.generate(
            instruction=f"""Validate the solution against the test cases:
            Function name: {function_name}
            Solution: {best_solution}
            Test cases: {self.problem_text}""",
            context=""
        )

        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Refine the solution to address validation issues:
                Issues: {validation}
                Original solution: {best_solution}""",
                context=best_solution
            )
            best_solution = refined_solution

        # Phase 4: Final Refinement
        final_code = await self.revise(
            instruction=f"""Ensure the code is clean, properly indented, and includes all necessary imports:
            Function name: {function_name}
            Solution: {best_solution}""",
            context=best_solution
        )

        return final_code