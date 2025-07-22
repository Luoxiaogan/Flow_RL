# Workflow ID: gsm8k_272_1
# Benchmark: gsm8k
# Data Indices: [227, 475]

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
        Reflect and Regenerate Workflow: Generate an initial solution, reflect on it critically to identify potential flaws or improvements, then use that reflection to guide a new, improved solution.
        This meta-cognitive loop mimics how humans refine their thinking — not just by fixing errors, but by understanding why the original approach might have been suboptimal.
        """
        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into smaller parts and solve each part systematically.")

        # Step 2: Critically reflect on the solution — do NOT rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted solution generation
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses the issues or opportunities identified in the reflection."
        )

        return final_solution