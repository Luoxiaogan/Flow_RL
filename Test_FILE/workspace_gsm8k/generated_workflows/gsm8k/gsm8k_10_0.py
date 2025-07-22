# Workflow ID: gsm8k_10_0
# Benchmark: gsm8k
# Data Indices: [547, 548, 343]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        This design explores multiple solution paths (parallel), selects the best one (ensemble),
        reflects critically on it, and then regenerates a superior answer guided by that reflection.
        """
        # Step 1: Generate 3 independent solutions using parallel ensemble pattern
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step. Break it into clear logical parts. Be precise with units and calculations."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the candidates
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the best solution — identify potential flaws, assumptions, or overlooked aspects
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution via FlexibleCustom
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with greater precision and attention to detail.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        return final_solution