# Workflow ID: gsm8k_67_1
# Benchmark: gsm8k
# Data Indices: [42, 96]

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
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It first generates an initial solution, then uses reflection to critique it,
        and finally creates a refined solution based on that critique — all in a single
        meta-cognitive loop. This avoids unnecessary parallelism or multiple iterations
        while ensuring robustness through internal self-awareness.
        
        Key difference from existing: Uses Reflect as a catalyst for improvement rather than just
        a diagnostic tool; combines Custom + Reflect + Custom in a structured feedback loop.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution to identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem incorporating these insights to improve accuracy and clarity."
        )

        return final_answer