# Workflow ID: gsm8k_24_0
# Benchmark: gsm8k
# Data Indices: [940, 729, 565]

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
        This is a diverse workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to produce a superior final answer.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply systematic problem-solving steps to analyze, plan, solve, and verify.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                       f"Re-solve the problem with this insight in mind. Be precise, logical, and thorough."
        )

        return final_solution