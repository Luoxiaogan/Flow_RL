# Workflow ID: gsm8k_226_1
# Benchmark: gsm8k
# Data Indices: [869, 845]

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
        Diverse and efficient workflow using Parallel Ensemble (Fan-out/Fan-in) with a single review step.
        This approach generates 3 independent solutions in parallel to handle uncertainty in reasoning paths,
        then selects the best one — robust against flawed initial logic while remaining simple and fast.
        """
        # Step 1: Generate multiple candidate solutions independently
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step. Be clear and precise in each reasoning step."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the candidates
        final_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: One final review to polish the selected solution — no reflection needed
        polished_solution = await self.review(pre_solution=final_solution)

        return polished_solution