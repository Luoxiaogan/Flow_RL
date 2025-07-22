# Workflow ID: gsm8k_301_1
# Benchmark: gsm8k
# Data Indices: [572, 386]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to identify weaknesses or missed opportunities, then use that reflection to guide a new, improved solution.
        This meta-cognitive loop mimics how humans improve reasoning — not just by fixing errors, but by understanding *why* the first attempt might have been flawed.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem into clear steps, solve each part logically, and verify your answer."
        )

        # Step 2: Critically reflect on the solution — do NOT rewrite it yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection on potential flaws or improvements: '{reflection}'. Now, provide a new, improved solution that addresses these points."
        )

        return final_solution