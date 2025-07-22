# Workflow ID: gsm8k_271_0
# Benchmark: gsm8k
# Data Indices: [296, 256, 298]

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
        This is a diverse and complex workflow combining:
        - Parallel Ensemble (fan-out) to generate multiple initial solutions
        - Reflect + Regenerate pattern to refine the best solution based on meta-cognition
        - Iterative Refinement for final polish
        """

        # Step 1: Generate multiple independent solutions using parallel ensemble
        solution_candidates = []
        for _ in range(3):  # Generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve the problem step-by-step. Break it into logical parts. Show all calculations clearly."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to pick the most accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the best solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new Custom call for an improved solution
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with these insights in mind. Be more precise and check your logic again."
        )

        # Step 5: Optional iterative refinement — review the improved solution one last time
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution