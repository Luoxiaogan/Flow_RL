# Workflow ID: gsm8k_197_1
# Benchmark: gsm8k
# Data Indices: [474, 752, 16]

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
        Reflect and Regenerate Workflow: Generate a solution, reflect on it to identify potential flaws or improvements, then use that reflection to guide a new, targeted solution.
        This approach leverages meta-cognition—critically analyzing one's own reasoning before generating a better answer—resulting in higher-quality outputs with minimal steps.
        """
        # Step 1: Generate an initial solution using a flexible custom approach with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using logical deduction and clear explanations.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "break_into_steps", "compute", "check"]
        )

        # Step 2: Critically reflect on the initial solution—identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution focused on addressing the identified issues
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nProvide a revised solution that addresses these points. Be precise and ensure all steps are logically sound."
        )

        return final_solution