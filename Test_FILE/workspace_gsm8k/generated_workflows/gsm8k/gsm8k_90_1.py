# Workflow ID: gsm8k_90_1
# Benchmark: gsm8k
# Data Indices: [755, 967]

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
        Reflect-and-Regenerate workflow: Generate an initial solution, critically reflect on it to uncover blind spots or assumptions,
        then use that reflection to guide a targeted, improved solution. This mimics human meta-cognition—learning from mistakes before finalizing.
        """
        # --- Step 1: Generate an initial solution using a structured approach ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear logical steps and justifying each one.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "validate_result"]
        )

        # --- Step 2: Critically reflect on the initial solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to generate a refined, higher-quality solution ---
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial attempt:\n{reflection}\n\n"
                       f"Re-solve the problem with deeper insight, addressing any gaps, errors, or oversights identified in the reflection."
        )

        return final_answer