# Workflow ID: gsm8k_162_0
# Benchmark: gsm8k
# Data Indices: [383, 218, 929]

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
        It first generates an initial solution, critically reflects on it, then uses that reflection
        to guide a more informed and improved final solution — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a refined instruction for a new solution
        refined_instruction = (
            f"Given the following reflection on the initial attempt: '{reflection}'. "
            "Now, provide a new, improved solution that addresses the identified issues. "
            "Be precise, logical, and thorough in your approach."
        )

        # Step 4: Generate the final solution based on the reflection
        final_solution = await self.custom(instruction=refined_instruction)

        return final_solution