# Workflow ID: gsm8k_180_1
# Benchmark: gsm8k
# Data Indices: [841, 282]

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
        Reflect and Regenerate Workflow: Generate an initial solution, reflect on it to uncover potential flaws or improvements, then use that reflection to guide a targeted re-solution.
        This approach leverages meta-cognition for efficient improvement without multiple iterations — balancing simplicity and effectiveness.
        """
        # Step 1: Generate an initial solution using structured reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step with clear logic. Break it into parts: knowns, unknowns, operations needed, and final answer."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, missing steps, or ambiguities
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a focused, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again with improved clarity, correctness, and completeness."
        )

        return final_solution