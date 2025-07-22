# Workflow ID: gsm8k_379_0
# Benchmark: gsm8k
# Data Indices: [85, 836]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Critically reflect on it to uncover potential flaws or improvements.
        4. Use that reflection to guide a new, targeted solution generation.
        This creates a meta-cognitive loop with robustness from diversity.
        """

        # Step 1: Parallel Ensemble — Generate multiple initial solutions
        solutions = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step using a different reasoning approach each time. Focus on clarity and logical progression."
            )
            solutions.append(sol)

        # Step 2: Select the best solution via ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect — Critique the selected solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate based on reflection — Use the critique as guidance
        final_instruction = (
            f"Based on the following reflection about the previous solution: '{reflection}'. "
            "Now, provide a revised and improved solution that addresses the identified concerns. "
            "Ensure all steps are clearly explained and logically sound."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution