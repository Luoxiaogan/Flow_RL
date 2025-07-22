# Workflow ID: gsm8k_164_1
# Benchmark: gsm8k
# Data Indices: [453, 813, 546]

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
        Reflect-and-Regenerate Workflow: Generate a solution, reflect on it to uncover hidden flaws or assumptions, then use that insight to craft a better solution.
        This meta-cognitive loop ensures the solver learns from its own reasoning — a fundamentally different approach from iterative refinement.
        It avoids redundant reviews by focusing on critical analysis before regenerating.
        """
        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify potential errors, missing steps, or unjustified assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a corrected and improved solution."
        )

        return final_solution