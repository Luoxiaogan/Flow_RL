# Workflow ID: gsm8k_290_1
# Benchmark: gsm8k
# Data Indices: [630, 741, 280]

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
        Diverse workflow using the 'Reflect and Regenerate' pattern with iterative refinement.
        This approach first generates a solution, reflects on it to uncover blind spots or inefficiencies,
        then uses that reflection to guide a more targeted, improved solution — all within a single meta-cognitive loop.
        Crucially, this avoids redundant full re-solves by leveraging structured reflection.
        """

        # Step 1: Generate an initial solution using step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, potential errors, or missed strategies
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, focused Custom call for improvement
        final_solution = await self.custom(
            instruction=f"Based on the following reflection on the initial solution: '{reflection}'. "
                        "Now, provide a refined answer that addresses these points. Be precise and avoid repeating the same mistakes."
        )

        return final_solution