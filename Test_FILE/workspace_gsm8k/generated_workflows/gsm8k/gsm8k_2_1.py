# Workflow ID: gsm8k_2_1
# Benchmark: gsm8k
# Data Indices: [914, 636, 904]

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
        and finally uses that reflection to guide a new, improved solution. This meta-cognitive loop enhances accuracy
        by incorporating self-awareness into the reasoning process — a fundamentally different logic from parallel ensembling.
        """
        # --- Step 1: Generate an initial solution using a general-purpose custom instruction ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly and thoroughly."
        )

        # --- Step 2: Use the Reflect operator to critique the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to guide a new, targeted Custom call for an improved solution ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, provide a revised and improved solution based on this insight. Focus on addressing any gaps, errors, or unclear reasoning identified in the reflection."
        )

        return final_answer