# Workflow ID: high_level_math_ganluo_10_0
# Benchmark: high_level_math_ganluo
# Data Indices: [24]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Problem Understanding and Decomposition
        decomposition = await self.generate(
            instruction="Analyze the problem thoroughly. Identify the key components, constraints, and the desired output. Break the problem into smaller sub-problems if possible.",
            context=self.problem_text
        )

        # Step 2: Parallel Exploration of Solution Paths
        results = await asyncio.gather(
            self.generate(
                instruction=f"Based on the decomposition: {decomposition}, solve the problem using algebraic reasoning. Focus on equations, inequalities, and functional relationships.",
                context=self.problem_text
            ),
            self.generate(
                instruction=f"Based on the decomposition: {decomposition}, solve the problem using combinatorial reasoning. Count arrangements, subsets, or configurations as needed.",
                context=self.problem_text
            ),
            self.generate(
                instruction=f"Based on the decomposition: {decomposition}, solve the problem using geometric reasoning. Consider areas, volumes, or coordinate transformations.",
                context=self.problem_text
            )
        )

        # Step 3: Evaluation and Synthesis
        best_solution = await self.ensemble(
            instruction="Compare the following candidate solutions. Select the one that is most mathematically rigorous, elegant, and satisfies all problem constraints. Provide justification for your choice.",
            contexts=results
        )

        # Step 4: Refinement (if necessary)
        refined_solution = await self.revise(
            instruction="Critique and improve the following solution. Ensure it is clear, correct, and complete. Address any ambiguities or errors.",
            context=best_solution
        )

        # Step 5: Final Verification
        final_summary = await self.summarize(
            instruction="Condense the solution into a concise and verifiable form. Ensure it includes all key steps and satisfies the problem's requirements.",
            context=refined_solution
        )

        return final_summary