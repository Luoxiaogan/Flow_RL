# Workflow ID: gsm8k_164_1
# Benchmark: gsm8k
# Data Indices: [182, 200, 137]

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
        Iterative Refinement with Reflective Guidance: 
        This workflow uses a reflective loop to guide improvements—not just blind refinement.
        Step 1: Generate an initial solution.
        Step 2: Reflect on its weaknesses (without rewriting).
        Step 3: Use that reflection to generate a more targeted second solution.
        Step 4: Review the second solution for final polish.
        This approach combines iterative improvement with meta-cognitive insight—more robust than pure repetition.
        """
        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused re-solution
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        "Now solve the problem again with improved clarity and logical rigor."
        )

        # Step 4: Final refinement via review to ensure correctness and completeness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution