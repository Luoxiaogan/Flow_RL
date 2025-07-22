# Workflow ID: gsm8k_225_1
# Benchmark: gsm8k
# Data Indices: [594, 716, 618]

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
        This is a diverse and robust workflow using the Reflect and Regenerate pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or improvements,
        and finally uses that reflection to guide a targeted regenerating step for a higher-quality answer.
        This mimics meta-cognitive reasoning: solve → evaluate → improve.
        """

        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly and logically."
        )

        # Step 2: Use Reflect to critique the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via Custom
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection:\n{reflection}\n\n"
                        "Now, provide a new, improved solution based on this reflection. Focus on addressing any weaknesses or assumptions noted."
        )

        return final_answer