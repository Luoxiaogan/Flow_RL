# Workflow ID: gsm8k_163_0
# Benchmark: gsm8k
# Data Indices: [108, 488, 661]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, critically reflects on it, and then uses that reflection
        to guide a more refined final solution — mimicking deep metacognitive reasoning.
        """
        # Step 1: Generate an initial solution using flexible custom with a sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what is given and what needs to be found.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "set_up_equations", "solve"]
        )

        # Step 2: Reflect critically on the initial solution — no rewriting yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nRevise your approach accordingly and provide a clear, accurate solution."
        )

        return final_solution