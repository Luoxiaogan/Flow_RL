# Workflow ID: gsm8k_298_1
# Benchmark: gsm8k
# Data Indices: [923, 822]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to identify potential flaws or improvements, then use that reflection to guide a new, improved solution.
        This pattern mimics human meta-cognition — not just solving, but thinking about how we solve. It ensures the final answer benefits from both initial reasoning and self-aware critique.
        """
        # Step 1: Generate an initial solution using structured reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Focus on identifying key quantities and operations."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a fresh, targeted generation of the final solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points."
        )

        return final_solution