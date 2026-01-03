# Workflow ID: limr_141_0
# Benchmark: limr
# Data Indices: [256, 206]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it into one of the following categories:
            - Geometry (e.g., shapes, angles, distances)
            - Number Theory (e.g., primes, modular arithmetic)
            - Algebra (e.g., equations, functions)
            - Combinatorics (e.g., counting, permutations)
            - Probability (e.g., events, distributions)
            Provide a detailed classification and identify key components.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        decomposition = await self.generate(
            instruction=f"""Based on the classification:
            {analysis}
            
            Decompose the problem into sub-problems. For each sub-problem:
            - Identify what needs to be solved
            - List relevant constraints or conditions
            - Suggest possible solution strategies""",
            context=analysis
        )

        # Step 3: Parallel Solution Attempts
        sub_problems = decomposition.split("\n\n")  # Assume sub-problems are separated by double newlines
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the following sub-problem:
                {sub_problem}
                
                Use appropriate mathematical techniques and provide detailed reasoning.""",
                context=sub_problem
            ) for sub_problem in sub_problems]
        )

        # Step 4: Validation and Feedback
        refined_solutions = []
        for attempt in solution_attempts:
            validation = await self.generate(
                instruction=f"""Validate the solution attempt:
                {attempt}
                
                Check for:
                - Logical consistency
                - Mathematical correctness
                - Completeness of reasoning""",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    {validation}""",
                    context=attempt
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(attempt)

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined attempts.
            Ensure the final answer is precise and adheres to the problem requirements.""",
            contexts_list=refined_solutions
        )

        return final_solution