# Benchmark: GSM8K
# Workflow ID: gsm8k_3
# Data Indices: [60, 61, 62]
# Generation Time: 2025-07-17 21:02:42
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
        This is a workflow graph that uses a Reflect and Regenerate pattern with an ensemble of solutions.
        It first generates multiple initial solutions, then evaluates them, and finally refines the best one.
        """

        # Step 1: Generate multiple initial solutions using different reasoning approaches
        solution1 = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
        solution2 = await self.custom(instruction="Break the problem into parts and solve each part independently.")
        solution3 = await self.custom(instruction="Use logical deduction to arrive at the answer.")

        # Step 2: Use ScEnsemble to select the best solution from the three generated ones
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Reflect on the selected solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final, refined solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        return final_solution