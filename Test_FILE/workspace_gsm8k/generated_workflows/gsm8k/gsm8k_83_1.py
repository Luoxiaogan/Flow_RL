# Workflow ID: gsm8k_83_1
# Benchmark: gsm8k
# Data Indices: [885, 311, 968]

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
        This is a diverse and robust workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or improvements,
        and finally uses that reflection to guide a new, improved solution. This mimics meta-cognitive reasoning.
        """

        # --- Step 1: Generate an initial solution using flexible custom with structured steps ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, clearly stating assumptions and calculations.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"],
            use_structured_output=True
        )

        # --- Step 2: Reflect critically on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to guide a new, more informed solution ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Revise the approach accordingly and provide a corrected, improved solution."
        )

        return final_answer