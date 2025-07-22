# Workflow ID: gsm8k_37_1
# Benchmark: gsm8k
# Data Indices: [525, 606]

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
        This workflow uses the 'Reflect and Regenerate' pattern — a fundamentally different logic from iterative refinement.
        It generates an initial solution, critically reflects on it to uncover hidden assumptions or gaps,
        then uses that reflection to guide a targeted re-solution. This mimics human meta-cognition: 
        not just fixing errors, but understanding why they occurred and how to avoid them in the next attempt.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning approach
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify potential flaws, oversights, or unclear logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution that addresses the identified issues
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a new, improved solution that corrects any flaws or ambiguities noted above."
        )

        return final_solution