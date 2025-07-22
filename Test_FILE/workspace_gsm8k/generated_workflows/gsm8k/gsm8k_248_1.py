# Workflow ID: gsm8k_248_1
# Benchmark: gsm8k
# Data Indices: [496, 457, 297]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to identify potential flaws or improvements, then use that reflection to guide a targeted re-generation of the final answer.
        
        This pattern mimics human meta-cognition—first solving, then stepping back to evaluate the solution's quality before crafting a better one. It avoids blind refinement (like Review-only) by introducing explicit critique as a catalyst for improvement.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Be precise and avoid assumptions."
        )

        # Step 2: Critically reflect on the initial solution—identify possible errors, missing steps, or alternative approaches
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following initial solution and reflection on its potential weaknesses: '{reflection}'. Now, provide a revised, more accurate, and complete solution based on this insight."
        )

        return final_solution