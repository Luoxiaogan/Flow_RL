# Benchmark: GSM8K
# Workflow ID: gsm8k_9
# Data Indices: [120, 121, 122]
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
        This is a diverse and structured workflow for solving mathematical problems.
        It uses a reflective loop with iterative refinement to ensure robustness and accuracy.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a revised solution
        revised_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Now, provide a new, improved solution that addresses any identified issues."
        )

        # Step 4: Review the revised solution to further refine it
        final_solution = await self.review(pre_solution=revised_solution)

        return final_solution