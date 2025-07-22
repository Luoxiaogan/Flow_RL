# Workflow ID: gsm8k_16_1
# Benchmark: gsm8k
# Data Indices: [720, 152]

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
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on its potential flaws, and then use that reflection to guide a new, improved solution.
        This pattern introduces meta-cognition — evaluating one's own reasoning before proceeding — which is more efficient than blind iteration.
        It avoids redundant refinement steps and instead uses targeted improvement based on critical self-assessment.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not skip any steps."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution that addresses the identified issues
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with improved clarity, accuracy, and completeness."
        )

        return final_solution