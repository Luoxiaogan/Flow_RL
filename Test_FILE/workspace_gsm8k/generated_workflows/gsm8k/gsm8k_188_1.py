# Workflow ID: gsm8k_188_1
# Benchmark: gsm8k
# Data Indices: [655, 750]

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
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on its weaknesses, then use that reflection to guide a targeted revision.
        This meta-cognitive loop improves accuracy by identifying blind spots before rewriting—more efficient than iterative refinement for many problems.
        """
        # Step 1: Generate an initial solution using general-purpose reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First identify what is being asked, then list known quantities, and finally compute the result."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points."
        )

        return final_solution