# Workflow ID: gsm8k_97_0
# Benchmark: gsm8k
# Data Indices: [734, 382]

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
        It first generates an initial solution, critically reflects on it, and then uses that reflection
        to guide a more refined final solution — mimicking human meta-cognition for improved accuracy.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with clear identification of knowns and unknowns, then apply logical steps to solve.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_logic", "compute_answer"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior, guided solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Now, provide a new, improved solution that addresses the identified weaknesses or gaps."
        )

        return final_solution