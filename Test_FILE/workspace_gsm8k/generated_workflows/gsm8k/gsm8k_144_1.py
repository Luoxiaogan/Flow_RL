# Workflow ID: gsm8k_144_1
# Benchmark: gsm8k
# Data Indices: [550, 681]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to uncover potential flaws or improvements, then use that reflection to guide a new, higher-quality solution.
        This approach emphasizes meta-cognition — learning from the first attempt to produce a better outcome — making it distinct from iterative refinement via Review alone.
        """

        # Step 1: Generate an initial solution using clear, structured reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break down the problem into its components. Perform calculations carefully. Then, summarize your findings."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new custom generation for improved accuracy
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with this insight in mind. Be more precise, address any assumptions or gaps identified, and ensure logical consistency."
        )

        return final_solution