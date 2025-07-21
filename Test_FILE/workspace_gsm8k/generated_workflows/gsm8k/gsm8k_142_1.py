# Workflow ID: gsm8k_142_1
# Benchmark: gsm8k
# Data Indices: [667, 301, 451]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to uncover hidden assumptions or gaps, then use that reflection to guide a targeted re-solution.
        This meta-cognitive approach mimics expert problem-solving where self-awareness drives improvement — a powerful alternative to iterative refinement.
        """
        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into clear logical steps and explain each one."
        )

        # Step 2: Critically reflect on the solution — identify potential flaws, oversights, or missing assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points explicitly."
        )

        return final_solution