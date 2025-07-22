# Workflow ID: gsm8k_22_1
# Benchmark: gsm8k
# Data Indices: [495, 807]

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
        Diverse workflow using the 'Parallel Ensemble' pattern with a single initial solution and one refinement.
        This approach generates multiple perspectives in parallel (via loop) to improve robustness without excessive complexity.
        It differs from the existing logic by introducing parallel exploration early and using ensemble selection.
        """
        # Step 1: Generate multiple candidate solutions in parallel using a simple loop
        solutions = []
        for _ in range(3):  # Generate 3 different approaches
            sol = await self.custom(
                instruction="Solve the problem step-by-step. Focus on clarity and logical structure."
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the best solution from the candidates
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Optionally refine the best solution once for final polish
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer