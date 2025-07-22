# Workflow ID: gsm8k_398_1
# Benchmark: gsm8k
# Data Indices: [185, 783]

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
        Reflect-and-Regenerate Workflow: Generate a solution, reflect on its weaknesses, then use that reflection to guide a new, improved solution.
        This approach leverages meta-cognition—critiquing the reasoning process itself—to produce higher-quality outputs without iterative refinement loops.
        It is efficient because it avoids redundant steps and uses reflection to directly inform the next attempt.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with this insight in mind."
        )

        return final_solution