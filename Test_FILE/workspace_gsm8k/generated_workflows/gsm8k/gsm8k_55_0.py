# Workflow ID: gsm8k_55_0
# Benchmark: gsm8k
# Data Indices: [846, 469]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It starts with an initial solution, reflects on it to identify potential flaws or improvements,
        then uses that insight to generate a final refined answer — all in under 5 steps.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with iterative reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using logical reasoning.",
            reasoning_pattern="iterative",
            steps=["understand", "analyze", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the initial solution to uncover assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted custom call for a better solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and rigor."
        )

        return final_solution