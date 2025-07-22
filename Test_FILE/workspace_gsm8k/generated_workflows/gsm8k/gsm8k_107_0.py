# Workflow ID: gsm8k_107_0
# Benchmark: gsm8k
# Data Indices: [648, 607, 567]

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
        to guide a new, improved solution — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, breaking down each component logically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_solution = await self.custom(
            instruction=f"Given the following initial solution and reflection:\n\n"
                        f"Initial Solution:\n{initial_solution}\n\n"
                        f"Reflection:\n{reflection}\n\n"
                        f"Provide a new, improved solution that addresses the concerns raised in the reflection."
        )

        return final_solution