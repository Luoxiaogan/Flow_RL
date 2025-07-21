# Workflow ID: gsm8k_112_1
# Benchmark: gsm8k
# Data Indices: [231, 302]

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
        It generates an initial solution, reflects on it to identify potential flaws or gaps,
        then uses that reflection to guide a new, improved solution — mimicking human meta-cognition.
        The structure avoids repetition of the existing iterative refinement approach
        and introduces a reflective loop for deeper reasoning.
        """
        # Step 1: Generate an initial solution with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        "Now, solve the problem again with this insight in mind. Be precise and thorough."
        )

        return final_solution