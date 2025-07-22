# Workflow ID: gsm8k_139_0
# Benchmark: gsm8k
# Data Indices: [841, 670, 812]

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
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to produce a superior, improved answer.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, breaking it into logical parts and explaining each step clearly."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, potential errors, or missing logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted Custom call for an improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        "Now, re-solve the problem with greater precision, addressing any weaknesses identified in the reflection. "
                        "Ensure your reasoning is thorough, accurate, and free of logical gaps."
        )

        return final_solution