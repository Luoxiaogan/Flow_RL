# Workflow ID: limr_30_0
# Benchmark: limr
# Data Indices: [59, 81]

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
            instruction="""Classify this problem:
            1. Identify the domain (geometry, number theory, etc.)
            2. Extract key entities, numbers, and relationships
            3. Determine the expected answer format
            Provide structured classification.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        solution_paths = await asyncio.gather(
            self.generate(instruction="Solve using geometric methods...", context=analysis),
            self.generate(instruction="Solve using algebraic methods...", context=analysis),
            self.generate(instruction="Solve using combinatorial methods...", context=analysis)
        )

        # Step 3: Iterative Refinement and Validation
        refined_solutions = []
        for solution in solution_paths:
            refined = await self.revise(
                instruction="Improve clarity, add specific calculations, and verify correctness...",
                context=solution
            )
            validation = await self.generate(
                instruction="Validate the refined solution...",
                context=refined
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined
                )
            refined_solutions.append(refined)

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="Synthesize all refined solutions into a unified final answer...",
            contexts_list=refined_solutions
        )

        # Step 5: Final Verification and Presentation
        verified_solution = await self.revise(
            instruction="Ensure all calculations are correct and present the final answer as an exact integer...",
            context=final_solution
        )

        return verified_solution