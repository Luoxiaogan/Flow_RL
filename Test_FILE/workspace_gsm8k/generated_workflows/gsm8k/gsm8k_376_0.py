# Workflow ID: gsm8k_376_0
# Benchmark: gsm8k
# Data Indices: [427, 369]

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
        Diverse and efficient workflow using iterative refinement with a flexible custom operator.
        This approach uses an iterative reasoning pattern to progressively improve the solution,
        leveraging structured steps without overcomplicating the logic — aligning with efficiency goals.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate a refined solution
        # The reasoning pattern is "iterative", meaning it will go through defined steps multiple times
        # until max_iterations (set to 2 here) or until convergence is implied by the steps
        solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze_problem", "formulate_plan", "execute_calculation", "verify_result"],
            max_iterations=2,
            custom_instruction="Solve the problem by breaking it into clear logical steps and refining your approach."
        )

        # Step 2: Review the final solution to catch any remaining errors or ambiguities
        final_solution = await self.review(pre_solution=solution)

        return final_solution