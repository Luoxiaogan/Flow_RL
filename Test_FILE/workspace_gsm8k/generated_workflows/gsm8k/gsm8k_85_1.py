# Workflow ID: gsm8k_85_1
# Benchmark: gsm8k
# Data Indices: [367, 543, 33]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Iterative Refinement.
        1. Generate an initial solution using FlexibleCustom in iterative mode to simulate step-by-step refinement.
        2. Use Reflect to critique the final iterative solution — not just for fixes, but to identify assumptions or blind spots.
        3. Regenerate a new solution based on reflection, incorporating meta-cognitive insights.
        4. Finally, apply a Review to polish clarity and correctness.
        
        This logic differs from the existing workflow by introducing a reflective loop that guides regeneration — not just ensembling multiple attempts — and uses iterative refinement as the core engine rather than parallel generation.
        """

        # --- Step 1: Iterative Refinement via FlexibleCustom ---
        # Use iterative reasoning pattern to build a solution through successive passes
        iterative_solution = await self.flexible_custom(
            custom_instruction="Solve this problem systematically by refining your approach over multiple iterations.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3
        )

        # --- Step 2: Reflect on the iterative solution to uncover hidden issues ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- Step 3: Regenerate a new solution informed by the reflection ---
        # This is the key difference: instead of ensembling, we use reflection to guide a fresh start
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection}'. "
                        f"Re-solve the problem now, focusing on addressing the identified limitations."
        )

        # --- Step 4: Final Review to ensure clarity and correctness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer