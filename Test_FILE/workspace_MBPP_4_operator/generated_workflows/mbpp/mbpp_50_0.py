# Workflow ID: mbpp_50_0
# Benchmark: mbpp
# Data Indices: [217]

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

        # Step 1: Analyze the problem and extract key components
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract the function name from the assert statements.
            - Identify input types and expected outputs.
            - Summarize the task description in structured form.
            Provide clear labels for each component.""",
            context=""
        )

        # Step 2: Generate an initial solution
        initial_solution = await self.generate(
            instruction=f"""Using the analysis:
            {analysis}
            
            Write Python code to solve the problem:
            - Include necessary imports at the top.
            - Ensure proper indentation and syntax.
            - Handle edge cases explicitly.""",
            context=analysis
        )

        # Step 3: Validate and refine the solution
        refined_solution = await self.revise(
            instruction=f"""Validate the solution:
            - Ensure it passes all test cases.
            - Check for missing imports or logical errors.
            - Improve readability and clarity where needed.
            
            Here is the current solution:
            {initial_solution}""",
            context=initial_solution
        )

        # Step 4: Explore alternative solutions in parallel
        alternatives = await asyncio.gather(
            self.generate(
                instruction=f"""Write a straightforward implementation:
                {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Write an optimized implementation using Python's standard library:
                {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Write a highly readable implementation prioritizing clarity:
                {analysis}""",
                context=analysis
            )
        )

        # Step 5: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness: Passes all test cases.
            - Efficiency: Optimized for performance.
            - Readability: Easy to understand and maintain.""",
            contexts_list=[refined_solution] + list(alternatives)
        )

        return final_solution