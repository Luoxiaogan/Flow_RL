# Workflow ID: mbpp_41_0
# Benchmark: mbpp
# Data Indices: [142, 332]

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

        # Step 1: Extract function name and parameters from test cases
        function_info = await self.generate(
            instruction="Extract the function name and parameters from the test cases. "
                        "Look for patterns like 'assert function_name(args) == expected_output'. "
                        "Return the function name and parameter types.",
            context=""
        )

        # Step 2: Parse task description to identify key requirements
        task_analysis = await self.generate(
            instruction=f"Analyze the task description to identify: "
                        f"1. Input types (e.g., list, string, integer). "
                        f"2. Output type (e.g., list, string, boolean). "
                        f"3. Key operations (e.g., rotation, conversion, filtering). "
                        f"4. Potential edge cases (e.g., empty input, invalid data). "
                        f"Use the following function info: {function_info}.",
            context=""
        )

        # Step 3: Generate multiple candidate solutions in parallel
        candidate_solutions = await asyncio.gather(
            self.generate(
                instruction=f"Generate a solution assuming strict input validation. "
                            f"Task analysis: {task_analysis}.",
                context=""
            ),
            self.generate(
                instruction=f"Generate a solution assuming lenient input handling. "
                            f"Task analysis: {task_analysis}.",
                context=""
            ),
            self.generate(
                instruction=f"Generate a solution focusing on performance optimization. "
                            f"Task analysis: {task_analysis}.",
                context=""
            )
        )

        # Step 4: Select the best solution using ensemble evaluation
        best_solution = await self.ensemble(
            instruction="Evaluate candidate solutions based on: "
                        "1. Clarity and readability. "
                        "2. Adherence to task requirements. "
                        "3. Robustness in handling edge cases. "
                        "Select the most promising solution.",
            contexts_list=candidate_solutions
        )

        # Step 5: Generate Python code for the selected solution
        python_code = await self.generate(
            instruction=f"Generate clean, executable Python code for the following solution: {best_solution}. "
                        f"Ensure proper imports, indentation, and syntax. Format the code as a markdown block.",
            context=""
        )

        # Step 6: Validate the generated code against test cases
        validation_result = await self.generate(
            instruction=f"Validate the following code against the test cases: {python_code}. "
                        f"Identify any errors or mismatches. Provide detailed feedback.",
            context=""
        )

        # Step 7: Refine the code iteratively if validation fails
        while "error" in validation_result.lower():
            refined_code = await self.revise(
                instruction=f"Refine the following code to fix identified issues: {python_code}. "
                            f"Validation feedback: {validation_result}.",
                context=python_code
            )
            python_code = refined_code
            validation_result = await self.generate(
                instruction=f"Re-validate the refined code: {python_code}.",
                context=""
            )

        # Final Output
        return python_code