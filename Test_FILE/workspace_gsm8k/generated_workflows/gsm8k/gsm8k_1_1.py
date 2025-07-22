# Workflow ID: gsm8k_1_1
# Benchmark: gsm8k
# Data Indices: [318, 497, 861]

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
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on it to uncover potential flaws or missed steps,
        then uses that reflection to guide a targeted refinement. This meta-cognitive loop ensures
        both efficiency and improved accuracy without unnecessary complexity.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Critically reflect on the solution — identify assumptions, missing logic, or unclear parts
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a focused instruction for a refined solution
        refined_instruction = f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and completeness."
        final_answer = await self.custom(instruction=refined_instruction)

        return final_answer