# Workflow ID: gsm8k_34_1
# Benchmark: gsm8k
# Data Indices: [757, 534]

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
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on its potential flaws, then use that insight to guide a new, improved solution.
        This meta-cognitive loop mimics how humans identify and fix reasoning errors — efficient, focused, and effective.
        """
        # Step 1: Generate an initial solution using structured reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step with clear logic."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a refined solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial approach: '{reflection}'. "
                        f"Re-solve the problem carefully, addressing these points. Provide a concise, accurate answer."
        )

        return final_solution