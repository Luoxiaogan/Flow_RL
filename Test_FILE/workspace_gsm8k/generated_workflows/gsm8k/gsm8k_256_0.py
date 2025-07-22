# Workflow ID: gsm8k_256_0
# Benchmark: gsm8k
# Data Indices: [237, 402]

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
        1. Generate 3 independent solutions via parallel ensemble (robustness).
        2. Select best solution using ScEnsemble.
        3. Reflect on the selected solution to uncover hidden flaws or missed assumptions.
        4. Use reflection to guide a new, improved Custom call for final answer.
        This creates a meta-cognitive loop that improves accuracy beyond simple iteration.
        """

        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Avoid shortcuts."
            )
            solution_candidates.append(candidate)

        # Step 2: Ensemle the candidates to pick the most accurate one
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, targeted solution generation
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial solution:\n\n{reflection}\n\nNow, provide a revised and improved solution that addresses these points. Be thorough and precise."
        )

        return final_answer