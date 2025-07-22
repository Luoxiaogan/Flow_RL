# Workflow ID: gsm8k_113_1
# Benchmark: gsm8k
# Data Indices: [130, 477, 785]

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
        It generates an initial solution, critically reflects on it to uncover hidden flaws or assumptions,
        then uses that reflection to guide a targeted re-generation of the solution.
        This meta-cognitive loop ensures deeper reasoning than a single pass.
        """

        # --- STEP 1: Generate an initial solution using flexible custom with sequential steps ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "formulate", "compute", "check"]
        )

        # --- STEP 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Use the reflection to generate a new, improved solution ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Based on this insight, solve the problem again with greater precision and attention to potential errors or oversights."
        )

        return final_answer