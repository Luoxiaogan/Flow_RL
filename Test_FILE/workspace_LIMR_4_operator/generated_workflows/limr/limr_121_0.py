# Workflow ID: limr_121_0
# Benchmark: limr
# Data Indices: [30, 153]

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

        # Step 1: Initial Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the main mathematical domain (geometry, algebra, etc.)
            - Extract key variables, constraints, and relationships
            - Classify the problem type (e.g., optimization, proof, calculation)
            - Highlight any special conditions or requirements
            Provide structured output.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        decomposition = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Break the problem into sub-problems:
            - Define each sub-problem clearly
            - Specify dependencies between sub-problems
            - Identify required techniques for each sub-problem""",
            context=analysis
        )

        # Step 3: Parallel Exploration
        sub_problems = decomposition.split("\n")
        solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve this sub-problem using appropriate techniques: {sub}",
                context=decomposition
            ) for sub in sub_problems]
        )

        # Step 4: Iterative Refinement
        refined_solutions = []
        for sol in solutions:
            refined = await self.revise(
                instruction="Critique and improve this solution. Ensure all steps are clear and correct.",
                context=sol
            )
            refined_solutions.append(refined)

        # Step 5: Final Synthesis and Validation
        final_solution = await self.ensemble(
            instruction="""Synthesize the solutions to sub-problems into a final answer:
            - Ensure consistency across all sub-problems
            - Validate against original problem constraints
            - Confirm the answer is an exact integer between 000 and 999""",
            contexts_list=refined_solutions
        )

        return final_solution