# Benchmark: GSM8K
# Workflow ID: gsm8k_12
# Data Indices: [150, 151, 152]
# Generation Time: 2025-07-17 21:02:46
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
        This is a diverse and structured workflow for solving mathematical problems.
        It combines iterative refinement with reflection and ensemble selection.
        """

        # Step 1: Generate an initial solution using custom reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential flaws or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Provide a new, improved solution."
        )

        # Step 4: Review the refined solution to further improve it
        revised_solution = await self.review(pre_solution=refined_solution)

        # Step 5: Generate multiple alternative solutions using parallel ensembles
        solution_list = [
            await self.custom(instruction="Solve the problem from a different perspective.")
            for _ in range(3)  # Generate 3 alternative solutions
        ]

        # Step 6: Use ScEnsemble to select the best solution among the alternatives
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution