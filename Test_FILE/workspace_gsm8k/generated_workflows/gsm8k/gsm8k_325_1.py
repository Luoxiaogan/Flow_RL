# Workflow ID: gsm8k_325_1
# Benchmark: gsm8k
# Data Indices: [14, 860, 335]

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
        It generates an initial solution, critically reflects on it to uncover hidden assumptions or errors,
        then uses that reflection to guide a targeted revision — mimicking human meta-cognition.
        This logic differs fundamentally from the existing parallel ensemble by emphasizing internal critique
        and iterative improvement via reflection rather than external comparison.
        """

        # --- Step 1: Generate an initial solution using a flexible custom approach ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning. Do not optimize for speed — prioritize correctness.",
            reasoning_pattern="sequential",
            steps=["understand", "break_down", "solve", "check"]
        )

        # --- Step 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to guide a new, improved solution ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be more precise and avoid previous mistakes."
        )

        return final_answer