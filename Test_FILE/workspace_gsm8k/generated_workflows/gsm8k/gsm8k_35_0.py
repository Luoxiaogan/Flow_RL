# Workflow ID: gsm8k_35_0
# Benchmark: gsm8k
# Data Indices: [880, 635]

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
        self.reflect = operator.Reflect(self.config, self.problem) # New operator
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        """
        This is a robust, diverse workflow using the Parallel Ensemble pattern.
        Generates 3 distinct solutions via varied instructions and ensembles them.
        Final review ensures clarity and correctness.
        """
        solutions = []

        # Generate three different approaches using Custom with varied prompts
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by breaking the problem into known quantities and unknowns. Focus on identifying what must be calculated first."
            elif i == 1:
                instruction = "Use a structured approach: list all given values, define variables, write equations, then solve. Be explicit about each step."
            else:
                instruction = "Start with an estimation or intuitive guess, then verify it mathematically. Explain your reasoning clearly."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Enforce consistency across multiple reasoning paths
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final refinement to polish clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer