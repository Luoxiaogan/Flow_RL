# Benchmark: GSM8K
# Workflow ID: gsm8k_3
# Data Indices: [60, 61, 62]
# Generation Time: 2025-07-17 22:42:08
# Status: generated
# ==================================================

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

    async def run_workflow(self):
        """
        A complex workflow combining Parallel Ensemble and Reflect-and-Regenerate patterns.
        """
        # Step 1: Generate multiple initial solutions in parallel
        solution_list = []
        for _ in range(3):  # Generate 3 different initial solutions
            solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new Custom call with improved instructions
        improved_instruction = f"Based on the following reflection: {reflection}. Now, solve the problem again, incorporating these insights."
        final_solution = await self.custom(instruction=improved_instruction)

        # Step 5: Optionally review the final solution for further refinement
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution