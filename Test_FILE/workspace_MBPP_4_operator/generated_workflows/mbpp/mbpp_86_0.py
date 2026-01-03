# Workflow ID: mbpp_86_0
# Benchmark: mbpp
# Data Indices: [28, 137]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem text and test cases:
            1. Extract the function name from the assert statements.
            2. Identify the input types and expected outputs.
            3. Summarize the task requirements in structured form.""",
            context=""
        )

        # Extract function name using regex
        function_name_match = re.search(r"assert\s+(\w+)\(", self.problem_text)
        function_name = function_name_match.group(1) if function_name_match else "solution"

        # Step 2: Parallel Exploration
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using direct translation:
                - Translate the task description into Python code.
                - Use basic constructs like loops and conditionals.
                - Ensure the function name is '{function_name}'.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                - Leverage Python's built-in libraries where applicable.
                - Optimize for readability and efficiency.
                - Ensure the function name is '{function_name}'.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using recursive decomposition:
                - Break the problem into smaller sub-problems.
                - Use recursion to solve each sub-problem.
                - Ensure the function name is '{function_name}'.""",
                context=initial_analysis
            )
        )

        # Step 3: Synthesis and Selection
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on:
            - Correctness: Does it satisfy the test cases?
            - Clarity: Is the code easy to understand?
            - Efficiency: Does it use optimal algorithms?""",
            contexts_list=solution_attempts
        )

        # Step 4: Validation and Refinement
        max_iterations = 3
        for _ in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                - Check if all assert statements pass.
                - Identify any errors or edge cases.""",
                context=best_solution
            )
            if "error" in validation.lower():
                best_solution = await self.revise(
                    instruction=f"""Refine the solution:
                    - Fix identified errors.
                    - Address missing edge cases.
                    - Maintain proper formatting.""",
                    context=best_solution
                )
            else:
                break

        # Step 5: Final Output
        final_code = f"""{best_solution}"""
        return final_code