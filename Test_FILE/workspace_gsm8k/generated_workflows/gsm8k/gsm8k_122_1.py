# Workflow ID: gsm8k_122_1
# Benchmark: gsm8k
# Data Indices: [766, 449, 307]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This workflow uses the Parallel Ensemble pattern with a single iteration — 
        generating multiple independent solutions and selecting the best one. 
        It avoids iterative refinement or reflection loops, instead relying on diversity of initial approaches.
        This is logically distinct from the existing workflow which uses a single solution + reflection loop.
        """
        # Generate 3 different solutions using varied instructions to encourage diverse reasoning paths
        solution1 = await self.custom(instruction="Solve this step-by-step by first identifying all given quantities and then computing totals.")
        solution2 = await self.custom(instruction="Break the problem into parts: compute each component separately (e.g., hourly pay, tips) before summing.")
        solution3 = await self.custom(instruction="Use a structured approach: list knowns, unknowns, formulas, and calculations in order.")

        # Combine all solutions and let ScEnsemble pick the most accurate one
        solutions = [solution1, solution2, solution3]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution