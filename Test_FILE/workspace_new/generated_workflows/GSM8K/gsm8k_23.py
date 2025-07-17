# Benchmark: GSM8K
# Workflow ID: gsm8k_23
# Data Indices: [260, 261, 262]
# Generation Time: 2025-07-17 20:55:22
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
        This is a workflow graph that uses a hybrid approach of parallel reasoning and reflection.
        It generates multiple solutions, reflects on them, and then refines the best one.
        """

        # Step 1: Generate multiple initial solutions using parallel reasoning
        solution1 = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
        solution2 = await self.custom(instruction="Approach the problem from a different angle, focusing on unit conversions and proportions.")
        solution3 = await self.custom(instruction="Break the problem into smaller parts and solve each part individually.")

        # Step 2: Use ScEnsemble to select the most promising solution
        candidate_solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Reflect on the best solution to identify potential issues or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final, refined solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: {reflection}. "
                        "Use this insight to provide a more accurate and well-reasoned answer."
        )

        return final_solution