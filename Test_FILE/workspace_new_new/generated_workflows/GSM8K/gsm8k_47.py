# Benchmark: GSM8K
# Workflow ID: gsm8k_47
# Data Indices: [500, 501, 502]
# Generation Time: 2025-07-17 21:02:47
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
        self.reflect = operator.Reflect(self.config, self.problem)  # New operator

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        # Step 1: Generate initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution
        revised_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Please provide a new, improved solution based on this reflection."
        )

        # Step 4: Optionally refine further using Review
        refined_solution = await self.review(pre_solution=revised_solution)

        # Step 5: Generate a second independent solution for ensemble comparison
        second_solution = await self.custom(
            instruction="Solve the problem from scratch, using a different approach."
        )

        # Step 6: Use ScEnsemble to pick the best solution from multiple attempts
        best_solution = await self.sc_ensemble(solutions=[refined_solution, second_solution])

        return best_solution