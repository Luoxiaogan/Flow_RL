# Workflow ID: gsm8k_361_1
# Benchmark: gsm8k
# Data Indices: [470, 953, 573]

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
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Reflect-and-Regenerate Workflow: Generate a solution, reflect on its weaknesses, then use that insight to craft a targeted improvement.
        This meta-cognitive loop mimics how humans identify blind spots and refine their reasoning—efficient and effective for complex problems.
        Uses only two steps: one reflection + one custom call based on it. Avoids redundant iterations or ensemble overhead.
        """
        # Step 1: Generate an initial solution with clear, step-by-step instructions
        initial_solution = await self.custom(instruction="Solve the problem by breaking it into logical steps. Explain each step clearly.")

        # Step 2: Critically reflect on the solution — identify potential flaws, assumptions, or missing elements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, focused solution attempt
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution:\n{reflection}\n\nRevise the approach to address these concerns while solving the problem accurately."
        )

        return final_solution