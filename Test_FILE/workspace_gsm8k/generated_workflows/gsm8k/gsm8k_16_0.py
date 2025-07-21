# Workflow ID: gsm8k_16_0
# Benchmark: gsm8k
# Data Indices: [194, 553, 435]

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
        It first generates an initial solution, then critically reflects on it to guide a better final answer.
        """
        # Step 1: Generate an initial solution using a flexible custom approach with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what needs to be calculated, then break the problem into clear steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "set_up_equations", "solve"]
        )

        # Step 2: Reflect critically on the initial solution — find assumptions, potential errors, or missing elements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following initial solution:\n{initial_solution}\n\nAnd this reflection on its limitations:\n{reflection}\n\nNow provide a revised, more accurate solution."
        )

        return final_solution