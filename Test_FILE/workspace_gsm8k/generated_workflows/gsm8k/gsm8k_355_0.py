# Workflow ID: gsm8k_355_0
# Benchmark: gsm8k
# Data Indices: [586, 645]

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
        It generates an initial solution, critically reflects on it, and uses that reflection
        to guide a more refined final answer — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, breaking it into smaller parts and showing all calculations clearly."
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, missing steps, or assumptions
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a new, improved solution via a flexible custom call
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with this critique in mind. Ensure clarity, accuracy, and completeness."
        )

        return final_solution