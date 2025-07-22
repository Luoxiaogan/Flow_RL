# Workflow ID: gsm8k_155_1
# Benchmark: gsm8k
# Data Indices: [894, 944, 292]

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
        This is a diverse and robust workflow using the Reflect and Regenerate pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or improvements,
        and finally uses that reflection to guide a new, higher-quality solution.
        This meta-cognitive loop ensures deeper reasoning and better accuracy than a single pass.
        """

        # --- STEP 1: Generate an initial solution using flexible custom with sequential reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, explaining each part clearly.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # --- STEP 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Use the reflection to generate a refined solution ---
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Provide a new, improved solution based on this critical feedback."
        )

        # --- STEP 4: Final review to polish clarity and correctness ---
        polished_answer = await self.review(pre_solution=final_solution)

        return polished_answer