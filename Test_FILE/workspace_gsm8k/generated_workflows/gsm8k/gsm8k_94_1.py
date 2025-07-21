# Workflow ID: gsm8k_94_1
# Benchmark: gsm8k
# Data Indices: [738, 837]

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
        Efficient reflective refinement workflow: 
        1. Generate an initial solution with structured reasoning.
        2. Reflect on potential flaws or oversights.
        3. Use reflection to guide a targeted re-solution.
        4. Final review for clarity and correctness.
        This avoids ensemble complexity while ensuring depth through meta-cognition.
        """
        # Step 1: Initial solution using FlexibleCustom with sequential pattern for structured thinking
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear logical progression.",
            reasoning_pattern="sequential",
            steps=["understand", "model", "solve", "verify"]
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a focused, improved solution
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Provide a revised, more accurate solution that addresses the identified issues."
        )

        # Step 4: Final review to ensure clarity and correctness
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer