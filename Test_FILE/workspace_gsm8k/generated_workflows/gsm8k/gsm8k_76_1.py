# Workflow ID: gsm8k_76_1
# Benchmark: gsm8k
# Data Indices: [284, 925, 323]

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
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on its potential flaws, then use that insight to craft a better solution.
        This approach leverages meta-cognition — identifying weaknesses in reasoning before re-solving — leading to higher accuracy with minimal steps.
        """
        # Step 1: Generate an initial solution using flexible custom for structured thinking
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step, explaining each part clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with this insight in mind. Be precise and avoid repeating the same mistakes."
        )

        return final_solution