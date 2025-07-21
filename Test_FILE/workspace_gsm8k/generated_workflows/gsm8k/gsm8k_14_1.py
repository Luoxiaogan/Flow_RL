# Workflow ID: gsm8k_14_1
# Benchmark: gsm8k
# Data Indices: [311, 656]

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
        This is a novel workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a targeted revision — mimicking
        human meta-cognition. This approach prioritizes deep reasoning over brute-force
        ensembling, making it more efficient and insightful for problems requiring conceptual clarity.
        """
        # --- Step 1: Generate an initial solution with clear step-by-step reasoning ---
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into logical steps and explaining each one clearly."
        )

        # --- Step 2: Reflect on the initial solution — identify assumptions, gaps, or potential errors ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to generate a refined solution — this is where insight happens ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with improved clarity, correctness, and completeness."
        )

        return final_answer