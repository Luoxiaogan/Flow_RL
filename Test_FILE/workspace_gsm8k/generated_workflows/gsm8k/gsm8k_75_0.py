# Workflow ID: gsm8k_75_0
# Benchmark: gsm8k
# Data Indices: [889, 812]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect and Regenerate pattern to improve the best solution using meta-cognition
        3. Iterative Refinement on the regenerated solution for final polish
        """
        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_pool = []
        for i in range(3):  # Generate 3 different approaches
            instruction = "Solve the problem by first identifying key constraints and then applying logical deduction step-by-step."
            solution = await self.custom(instruction=instruction)
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to select the most promising candidate
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the selected solution — identify potential flaws or missed angles
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new custom generation for an improved solution
        improved_instruction = f"Based on the following reflection about the previous solution:\n{reflection}\nNow, provide a refined answer that addresses these points explicitly."
        final_solution = await self.custom(instruction=improved_instruction)

        # Step 5: Apply iterative refinement to ensure clarity, correctness, and completeness
        refined_final = await self.review(pre_solution=final_solution)

        return refined_final