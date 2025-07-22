# Workflow ID: gsm8k_259_1
# Benchmark: gsm8k
# Data Indices: [306, 688]

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
        This is a diverse and efficient workflow using the Iterative Refinement + Reflect-and-Regenerate pattern.
        It first generates multiple candidate solutions in parallel (fan-out), then refines them iteratively,
        while using reflection to guide improvements — fundamentally different from the existing single-path logic.
        """
        # Step 1: Generate 3 independent initial solutions via parallel ensemble
        solution_candidates = [
            await self.custom(instruction="Solve the problem step-by-step, focusing on clarity and logical flow."),
            await self.custom(instruction="Break the problem into subproblems and solve each systematically."),
            await self.custom(instruction="Use a structured approach: identify knowns, unknowns, constraints, then compute.")
        ]

        # Step 2: Use ScEnsemble to pick the best candidate as a starting point for refinement
        best_initial = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use the reflection to generate a new, improved solution with targeted guidance
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Revise the solution to address these points. Ensure all steps are logically sound and complete."
        )

        # Step 5: Apply iterative refinement — review the final solution one more time for polish
        polished_solution = await self.review(pre_solution=final_solution)

        return polished_solution