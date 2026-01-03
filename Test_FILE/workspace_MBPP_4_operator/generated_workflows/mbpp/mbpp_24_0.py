# Workflow ID: mbpp_24_0
# Benchmark: mbpp
# Data Indices: [65, 277]

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

        # Step 1: Analyze the problem
        analysis = await self.generate(
            instruction="""Extract the function name, input/output patterns, and constraints:
            - Parse test cases to identify the function name and argument structure.
            - Analyze the task description to understand requirements and infer edge cases.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Generate multiple initial solutions in parallel
        initial_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function based on the analysis:
                {analysis}
                
                Ensure the function adheres to Pythonic conventions and includes necessary imports.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an alternative Python function based on the analysis:
                {analysis}
                
                Explore a different approach to solving the problem.""",
                context=""
            )
        )

        # Step 3: Ensemble to select the best initial solution
        best_initial_solution = await self.ensemble(
            instruction="Select the most promising solution based on clarity, correctness, and adherence to requirements.",
            contexts_list=initial_solutions
        )

        # Step 4: Validate and refine iteratively
        refined_solution = best_initial_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                {refined_solution}
                
                Identify any errors or areas for improvement.""",
                context=""
            )
            if "error" not in validation.lower():
                break  # Stop if no errors are found
            refined_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                {validation}""",
                context=refined_solution
            )

        # Step 5: Handle edge cases
        edge_cases = await self.generate(
            instruction=f"""Identify potential edge cases based on the task description and test cases:
            {analysis}
            
            Generate additional test cases to validate robustness.""",
            context=""
        )
        final_solution = await self.revise(
            instruction=f"""Ensure the solution handles all edge cases:
            {edge_cases}""",
            context=refined_solution
        )

        # Step 6: Output final code
        return final_solution