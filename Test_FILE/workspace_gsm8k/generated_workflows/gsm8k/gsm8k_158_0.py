# Workflow ID: gsm8k_158_0
# Benchmark: gsm8k
# Data Indices: [563, 119]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate multiple solutions in parallel (fan-out).
        Step 2: Use ScEnsemble to select the best one.
        Step 3: Reflect on that solution to uncover hidden assumptions or errors.
        Step 4: Regenerate a new solution using the reflection as guidance.
        Step 5: Optionally, review the final answer for clarity and correctness.
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_pool = []
        for i in range(3):  # Generate 3 different initial approaches
            instruction = "Solve this math word problem by breaking it into clear steps. Consider different interpretations if applicable."
            sol = await self.custom(instruction=instruction)
            solution_pool.append(sol)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION ---
        regen_instruction = f"Given the following reflection on the previous solution: '{reflection_text}'. Now, provide an improved and more accurate solution based on this insight."
        final_answer = await self.custom(instruction=regen_instruction)

        # --- OPTIONAL REVIEW FOR FINAL CLARITY ---
        final_review = await self.review(pre_solution=final_answer)

        return final_review