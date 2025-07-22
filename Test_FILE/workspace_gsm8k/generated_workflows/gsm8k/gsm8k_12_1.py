# Workflow ID: gsm8k_12_1
# Benchmark: gsm8k
# Data Indices: [558, 286, 390]

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
        This workflow uses a reflective loop to guide iterative improvement — not just blind revision.
        First, generate an initial solution. Then, reflect on it to identify potential flaws or missing logic.
        Use that reflection to inform a second custom attempt, which is then reviewed for final polish.
        This ensures deeper metacognitive awareness than simple repetition.
        """
        # Step 1: Generate a clear, step-by-step initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be explicit about each calculation."
        )

        # Step 2: Critically reflect on the initial solution — don't rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        guided_solution = await self.custom(
            instruction=f"Given the following reflection on the initial approach: '{reflection}'. Now, solve the problem again with this insight in mind."
        )

        # Step 4: Final refinement using Review to polish clarity and correctness
        final_solution = await self.review(pre_solution=guided_solution)

        return final_solution