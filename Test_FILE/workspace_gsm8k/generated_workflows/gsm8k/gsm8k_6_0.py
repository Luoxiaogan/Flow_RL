# Workflow ID: gsm8k_6_0
# Benchmark: gsm8k
# Data Indices: [32, 494]

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
        This is a diverse workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to produce a superior, improved solution.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying all given relationships and unknowns in the problem.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "set_up_equations", "solve_system"]
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, assumptions, or missing logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted Custom call for a refined solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Reconstruct the answer carefully, ensuring logical completeness and accuracy. "
                        f"Break down each step clearly and verify consistency."
        )

        return final_solution