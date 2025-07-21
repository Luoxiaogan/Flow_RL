# Workflow ID: gsm8k_83_1
# Benchmark: gsm8k
# Data Indices: [823, 620]

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
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on it to uncover potential flaws or assumptions, then use that insight to craft a refined solution.
        This meta-cognitive loop improves accuracy by encouraging critical evaluation before re-solving — more efficient than iterative review for many problems.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts, show your work, and explain each step clearly."
        )

        # Step 2: Critically reflect on the solution — identify possible errors, missing assumptions, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with this feedback in mind."
        )

        return final_solution