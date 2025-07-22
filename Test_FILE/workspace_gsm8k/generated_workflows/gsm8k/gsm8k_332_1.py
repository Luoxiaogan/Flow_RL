# Workflow ID: gsm8k_332_1
# Benchmark: gsm8k
# Data Indices: [853, 373]

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
        This is a diverse and effective workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on it to identify potential flaws or improvements,
        then uses that reflection to guide a new, targeted solution — all in just 3 steps.
        This logic differs fundamentally from iterative refinement: instead of repeatedly fixing,
        it uses meta-cognition (reflection) to inform a single, better generation.
        """
        # Step 1: Generate an initial solution with clear reasoning instructions
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be thorough, but do not assume anything beyond what is stated."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and correctness."
        )

        return final_solution