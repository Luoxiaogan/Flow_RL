# Workflow ID: gsm8k_32_1
# Benchmark: gsm8k
# Data Indices: [798, 589, 79]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble + Reflect and Regenerate' pattern.
        It generates multiple initial solutions in parallel, selects the best one, then critically reflects on it
        before regenerating a superior final answer — combining robustness with meta-cognitive refinement.
        """

        # Step 1: Generate 3 independent solutions via FlexibleCustom in parallel (fan-out)
        # Each uses a different reasoning strategy to ensure diversity
        solutions = []
        for i in range(3):
            reasoning_pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem by focusing on clear steps and logical deduction.",
                reasoning_pattern=reasoning_pattern,
                steps=["analyze", "plan", "solve", "verify"],
                use_structured_output=True
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to guide a new, improved solution via Custom
        final_solution = await self.custom(
            instruction=f"Given the following solution and its reflection:\n\n"
                        f"Solution: {best_solution}\n\n"
                        f"Reflection: {reflection}\n\n"
                        f"Based on this insight, now provide a revised and more robust solution."
        )

        return final_solution