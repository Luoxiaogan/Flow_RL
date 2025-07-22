# Workflow ID: gsm8k_213_0
# Benchmark: gsm8k
# Data Indices: [846, 876, 857]

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
        First, generate an initial solution. Then critically reflect on it.
        Finally, use that reflection to guide a new, improved solution.
        """
        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a more informed and precise instruction for a new solution
        improved_instruction = f"Given the following reflection on the initial attempt: '{reflection}'. Now, solve the problem again with greater precision, ensuring all logical steps are sound and assumptions validated."

        # Step 4: Generate the final improved solution based on reflection
        final_solution = await self.custom(instruction=improved_instruction)

        return final_solution