# Workflow ID: gsm8k_28_0
# Benchmark: gsm8k
# Data Indices: [126, 326]

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
        It generates an initial solution, critically reflects on it, and then uses that reflection
        to produce a superior final answer — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and solve systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "identify_knowns", "set_up_equations", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        f"Re-solve the problem carefully, addressing any weaknesses or assumptions noted in the reflection. "
                        f"Provide a complete, step-by-step explanation of your improved reasoning."
        )

        return final_answer