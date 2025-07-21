# Workflow ID: gsm8k_78_1
# Benchmark: gsm8k
# Data Indices: [793, 571]

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
        Reflect and Regenerate Workflow: Generate an initial solution, reflect on its potential flaws or assumptions, then use that reflection to guide a new, improved solution.
        This meta-cognitive approach mimics how humans refine their reasoning — not just by editing, but by critically understanding why a solution might be flawed.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into smaller parts and solve step-by-step."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, missing logic, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution — now informed by insight, not just iteration
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. Now, provide a corrected and improved solution based on this analysis."
        )

        return final_solution