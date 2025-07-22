# Workflow ID: gsm8k_368_1
# Benchmark: gsm8k
# Data Indices: [903, 128]

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
        1. Generate an initial solution using FlexibleCustom in sequential mode for structured reasoning.
        2. Reflect on the solution to identify potential flaws or missed steps.
        3. Use that reflection to guide a new Custom call for a refined solution.
        4. Finally, apply iterative refinement via Review to polish the answer further.
        
        This logic differs from the existing workflow by:
        - Using Reflect as a critical meta-cognitive step before regeneration (not just post-hoc review).
        - Employing a two-stage improvement loop: first based on reflection, then manual refinement.
        - Avoiding parallel ensemble entirely — instead focusing on deep, guided iteration.
        """
        # --- Step 1: Generate initial structured solution using FlexibleCustom ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "compute", "verify"]
        )

        # --- Step 2: Reflect on the initial solution to uncover hidden assumptions or errors ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate a better solution using the reflection as guidance ---
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Re-solve the problem with greater attention to detail and logical rigor."
        )

        # --- Step 4: Apply iterative refinement to ensure clarity, correctness, and completeness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer