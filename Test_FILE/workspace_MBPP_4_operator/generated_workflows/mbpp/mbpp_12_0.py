# Workflow ID: mbpp_12_0
# Benchmark: mbpp
# Data Indices: [43, 221]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Extract the function name from the test cases.
            2. Classify the problem type (e.g., list operation, string manipulation).
            3. Identify key constraints and edge cases from the test cases.
            Provide structured output with clear sections.""",
            context=""
        )

        # Parse function name using regex
        function_name_match = re.search(r"assert\s+(\w+)\(", analysis)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Step 2: Parallel Solution Exploration
        strategies = [
            "Literal interpretation of the task description.",
            "Focus on satisfying test cases directly.",
            "Incorporate additional edge cases and constraints."
        ]
        candidate_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Generate a solution using this strategy: {strategy}",
                context=analysis
            ) for strategy in strategies]
        )

        # Step 3: Ensemble Selection
        selected_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Covers all test cases.
            - Avoids unnecessary complexity.
            - Is easy to understand and maintain.""",
            contexts_list=candidate_solutions
        )

        # Step 4: Code Refinement
        refined_code = await self.revise(
            instruction=f"""Refine the selected solution:
            - Add necessary imports.
            - Ensure proper indentation and formatting.
            - Handle edge cases explicitly.
            Original code:
            {selected_solution}""",
            context=analysis
        )

        # Step 5: Validation and Iteration
        for _ in range(3):  # Allow up to 3 refinement attempts
            validation = await self.generate(
                instruction="Validate the code against all test cases. Identify any errors.",
                context=refined_code
            )
            if "error" not in validation.lower():
                break
            refined_code = await self.revise(
                instruction=f"Fix issues: {validation}",
                context=refined_code
            )

        return refined_code