# Workflow ID: gsm8k_157_0
# Benchmark: gsm8k
# Data Indices: [460, 934, 680]

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
        It generates an initial solution, critically reflects on it, then uses that reflection
        to craft a superior final answer — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. First identify what is given, then determine what needs to be found, and finally apply appropriate mathematical operations."
        )

        # Step 2: Critically reflect on the initial solution
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised, more accurate, and logically sound solution based on this insight."
        )

        return final_solution