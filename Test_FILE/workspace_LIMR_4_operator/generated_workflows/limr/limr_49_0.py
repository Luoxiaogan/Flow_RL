# Workflow ID: limr_49_0
# Benchmark: limr
# Data Indices: [163, 125]

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

        # Step 1: Hierarchical Decomposition
        problem_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key components and relationships
            - Classify the problem type (geometry, algebra, combinatorics, etc.)
            - Highlight constraints and boundary conditions
            - Suggest potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        parallel_strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop solution using algebraic methods: {problem_analysis}",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"Develop solution using geometric methods: {problem_analysis}",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"Develop solution using combinatorial methods: {problem_analysis}",
                context=problem_analysis
            )
        )

        # Step 3: Iterative Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Refine solution: verify calculations, clarify reasoning, and address edge cases",
                context=solution
            ) for solution in parallel_strategies]
        )

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate correctness and completeness
            - Ensure alignment with problem constraints
            - Select the most elegant and efficient approach""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Verification and Condensation
        verified_solution = await self.revise(
            instruction="Verify final solution: check for errors, ensure precision, and confirm answer format",
            context=final_solution
        )
        concise_solution = await self.summarize(
            instruction="Condense solution into a clear and concise format",
            context=verified_solution
        )

        return concise_solution