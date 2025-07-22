# Workflow ID: gsm8k_49_0
# Benchmark: gsm8k
# Data Indices: [134, 806, 328]

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
        1. Parallel Ensemble (Fan-out) - Generate 3 independent solutions
        2. Reflect and Regenerate - Critique the best solution and regenerate
        3. Iterative Refinement - Apply one final review to polish the result
        """
        # Step 1: Generate multiple solutions in parallel using FlexibleCustom with "parallel" pattern
        solution_list = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem by breaking it into logical steps.",
                reasoning_pattern="parallel",
                steps=["analyze", "model", "compute", "verify"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from the parallel candidates
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to uncover hidden flaws or alternative approaches
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a new solution that incorporates insights
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Reconstruct the answer with improved clarity and logic."
        )

        # Step 5: Final refinement using Review to polish the improved solution
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer