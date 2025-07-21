# Workflow ID: gsm8k_77_1
# Benchmark: gsm8k
# Data Indices: [809, 703, 289]

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
        This workflow combines two powerful patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate multiple independent solutions to reduce single-point failure.
        2. Reflect-and-Regenerate: Critically analyze the best solution and refine it further for higher accuracy.

        The logic is:
        - Generate 3 diverse initial solutions using different reasoning styles.
        - Use ScEnsemble to pick the strongest one.
        - Reflect on that winner to uncover hidden flaws or assumptions.
        - Finally, regenerate a superior solution guided by the reflection — ensuring both robustness and depth.
        """

        # Step 1: Generate 3 parallel solutions with distinct reasoning approaches
        solution1 = await self.custom(instruction="Solve this math problem using a step-by-step arithmetic approach.")
        solution2 = await self.custom(instruction="Solve this problem using algebraic reasoning: define variables and equations first.")
        solution3 = await self.custom(instruction="Break the problem into smaller sub-problems, solve each independently, then combine.")

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        candidate_solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Reflect critically on the best solution to identify potential blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the best solution: '{reflection}', "
                        "generate a revised answer that addresses any identified weaknesses or missing elements."
        )

        return final_solution