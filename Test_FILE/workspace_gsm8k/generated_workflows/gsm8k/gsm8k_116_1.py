# Workflow ID: gsm8k_116_1
# Benchmark: gsm8k
# Data Indices: [491, 348]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble + Reflect and Regenerate' pattern.
        It first generates multiple independent solutions (parallel ensemble), then selects the best one,
        reflects on it critically, and finally regenerates a superior solution based on that reflection — 
        combining robustness with meta-cognitive refinement.
        """
        # Step 1: Generate 3 independent solutions using parallel reasoning (fan-out)
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction=f"Generate a unique approach to solving this problem. Focus on clarity and logical structure. "
                            f"This is attempt #{i+1}."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the candidates
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution via flexible custom reasoning
        final_solution = await self.flexible_custom(
            custom_instruction="Based on the reflection provided, generate a refined, structured, and accurate solution.",
            previous_results=[reflection]
        )

        return final_solution