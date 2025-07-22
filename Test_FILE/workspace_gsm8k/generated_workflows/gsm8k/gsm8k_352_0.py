# Workflow ID: gsm8k_352_0
# Benchmark: gsm8k
# Data Indices: [629, 229, 531]

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
        2. Reflect and Regenerate pattern: use reflection to guide improvement
        3. Iterative Refinement to polish the final answer
        """
        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_list = []
        for _ in range(3):  # Generate 3 different approaches
            sol = await self.custom(instruction="Solve the problem by breaking it into steps and reasoning clearly. Consider multiple strategies.")
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to select the best initial solution
        best_initial = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect critically on the selected solution
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Based on reflection, regenerate with improved focus
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now, re-solve the problem focusing on addressing these points while maintaining clarity and logical rigor."
        )

        # Step 5: Apply iterative refinement to polish the result
        refined_solution = await self.review(pre_solution=improved_solution)

        return refined_solution