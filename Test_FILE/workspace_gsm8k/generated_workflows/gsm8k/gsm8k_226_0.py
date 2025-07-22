# Workflow ID: gsm8k_226_0
# Benchmark: gsm8k
# Data Indices: [869, 845]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This structure allows for self-critique and refinement in a single loop — balancing simplicity with meta-cognitive improvement.
        """
        # Step 1: Initial solution via iterative flexible custom (3 steps: analyze, solve, verify)
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "verify"],
            max_iterations=1,
            custom_instruction="Begin by understanding the problem structure. Then solve it step-by-step. Finally, check your work for consistency."
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or missed details
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a new attempt — this is the core of the diverse pattern
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nRevise your solution accordingly to improve accuracy and completeness."
        )

        return final_solution