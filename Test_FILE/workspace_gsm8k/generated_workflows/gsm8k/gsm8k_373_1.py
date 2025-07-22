# Workflow ID: gsm8k_373_1
# Benchmark: gsm8k
# Data Indices: [105, 201]

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
        Diverse and efficient workflow using Parallel Ensemble + Reflect.
        This approach generates multiple independent solutions first, then uses reflection to guide a final synthesis.
        It differs from the existing logic by prioritizing parallel exploration before meta-cognitive refinement.
        """
        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        solution_candidates = []
        for _ in range(3):  # Generate 3 different initial approaches
            candidate = await self.custom(
                instruction="Solve this math problem step-by-step. Think about it in a unique way each time."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to select the best-performing candidate
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the best candidate to uncover hidden flaws or missed angles
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Synthesize a final improved solution based on the reflection
        final_solution = await self.custom(
            instruction=f"Using the following reflection: '{reflection}'. "
                       f"Refine the best solution below to ensure accuracy and completeness: {best_candidate}"
        )

        return final_solution