# Workflow ID: gsm8k_241_1
# Benchmark: gsm8k
# Data Indices: [216, 161]

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
        This workflow uses a reflective loop to guide improvements — not just blind refinement.
        Step 1: Generate initial solution.
        Step 2: Reflect on it to identify potential flaws or assumptions.
        Step 3: Use that reflection to craft a better custom prompt for a revised solution.
        Step 4: Repeat once more for deeper improvement — mimicking human metacognition.
        
        Key difference from existing: Instead of pure iterative review, this uses reflection as a catalyst for targeted revision.
        """
        # Step 1: Initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and explain each step clearly."
        )

        # Step 2: Critically reflect on the solution — no rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to generate a new, improved solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on an initial attempt: {reflection}. "
                        f"Use this insight to provide a more accurate and complete solution."
        )

        # Step 4: Second round — reflect again to catch remaining issues
        second_reflection = await self.reflect(pre_solution=refined_solution)

        # Step 5: Final refinement using the second reflection
        final_solution = await self.custom(
            instruction=f"Based on the reflection below, produce a fully corrected and polished solution: {second_reflection}"
        )

        return final_solution