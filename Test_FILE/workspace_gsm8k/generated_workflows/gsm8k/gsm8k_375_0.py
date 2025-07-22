# Workflow ID: gsm8k_375_0
# Benchmark: gsm8k
# Data Indices: [585, 844]

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
        This is a diverse and effective workflow using the Iterative Refinement pattern.
        It starts with a basic solution, then applies Review at least twice to progressively improve it.
        The structure ensures logical flow while maintaining generality across math problems.
        """
        # Step 1: Generate an initial solution using a simple, clear instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what needs to be calculated. Then, perform the calculation. Finally, state the answer clearly."
        )

        # Step 2: Apply iterative refinement — review the solution once
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Review again for deeper improvement (e.g., checking logic, clarity, completeness)
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Use Reflect to analyze potential weaknesses in the final refined solution
        reflection = await self.reflect(pre_solution=second_refined)

        # Step 5: Optionally generate one more improved version based on reflection (optional but aligns with meta-cognition)
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now, provide a final, polished answer that addresses all concerns raised in the reflection."
        )

        return final_solution