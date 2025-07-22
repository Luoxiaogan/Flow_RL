# Workflow ID: gsm8k_58_1
# Benchmark: gsm8k
# Data Indices: [224, 300, 679]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble + Reflect and Regenerate' hybrid pattern.
        It first generates multiple independent solutions (parallel), then uses reflection to guide refinement of the best one — combining robustness with meta-cognitive improvement.
        This differs fundamentally from the existing workflow by introducing parallelism before reflection, ensuring diverse reasoning paths are explored before deepening any single one.
        """

        # Step 1: Generate multiple candidate solutions in parallel using FlexibleCustom with "parallel" pattern
        # Each solution follows the same structured steps but may approach the problem differently due to prompt variation
        solutions = []
        for i in range(3):  # Generate 3 different approaches
            sol = await self.flexible_custom(
                custom_instruction=f"Approach this problem from a different perspective each time. Focus on clarity and logical structure.",
                reasoning_pattern="parallel",
                steps=["understand", "analyze", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the strongest candidate based on internal consistency and logic
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover potential blind spots or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to regenerate a superior final answer — now guided by both ensemble selection AND critical reflection
        final_solution = await self.custom(
            instruction=f"Given the following solution (selected as best via ensemble): {best_solution}\n\n"
                        f"And the following reflection highlighting possible improvements: {reflection}\n\n"
                        f"Provide a new, improved solution that addresses these concerns while maintaining clarity and correctness."
        )

        return final_solution