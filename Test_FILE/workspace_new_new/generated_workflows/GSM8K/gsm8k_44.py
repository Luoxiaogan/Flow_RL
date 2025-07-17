# Benchmark: GSM8K
# Workflow ID: gsm8k_44
# Data Indices: [470, 471, 472]
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
        This is a workflow graph that uses a Reflect-Regenerate loop with an ensemble of solutions.
        It first generates multiple initial solutions, then reflects on them, and finally regenerates a refined solution.
        """

        # Step 1: Generate multiple initial solutions using parallel ensembling
        initial_solutions = [
            await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly."),
            await self.custom(instruction="Break down the problem into logical parts and solve systematically."),
            await self.custom(instruction="Use algebraic reasoning to model the problem and find the answer.")
        ]

        # Step 2: Use ScEnsemble to select the best initial solution
        best_initial_solution = await self.sc_ensemble(solutions=initial_solutions)

        # Step 3: Reflect on the best solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_initial_solution)

        # Step 4: Regenerate a refined solution based on the reflection
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the solution: {reflection}. Now, provide a new, improved solution."
        )

        return final_solution