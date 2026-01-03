# Workflow ID: mbpp_28_0
# Benchmark: mbpp
# Data Indices: [290, 212]

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

        # Step 1: Extract function name and input types
        function_info = await self.generate(
            instruction="""Extract the function name and input types from the test cases.
            Focus on the assert statements to identify:
            - Function name
            - Argument types
            - Expected output format""",
            context=""
        )

        # Step 2: Analyze natural language description
        analysis = await self.generate(
            instruction="""Analyze the natural language description to understand:
            - Key operations required
            - Constraints and conditions
            - Potential edge cases""",
            context=function_info
        )

        # Step 3: Explore multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop a solution using mathematical computation.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a solution using string manipulation.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a solution using standard library functions.",
                context=analysis
            )
        )

        # Step 4: Select the best strategy
        best_strategy = await self.ensemble(
            instruction="Choose the most appropriate solution strategy based on clarity, correctness, and efficiency.",
            contexts_list=strategies
        )

        # Step 5: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the selected strategy:
            - Include necessary imports
            - Use proper indentation
            - Ensure the function name matches the test cases
            Selected strategy: {best_strategy}""",
            context=""
        )

        # Step 6: Validate and refine the code
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction="Validate the code against the test cases and identify issues.",
                context=initial_code
            )
            if "error" not in validation.lower():
                break  # Exit loop if no errors
            initial_code = await self.revise(
                instruction=f"Fix the following issues: {validation}",
                context=initial_code
            )

        # Step 7: Summarize and finalize the solution
        final_solution = await self.summarize(
            instruction="Condense the final solution into a clean, executable Python code block.",
            context=initial_code
        )

        return final_solution