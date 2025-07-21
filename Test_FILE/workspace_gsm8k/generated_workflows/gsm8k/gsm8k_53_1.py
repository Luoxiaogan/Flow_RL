# Workflow ID: gsm8k_53_1
# Benchmark: gsm8k
# Data Indices: [775, 160, 741]

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
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a new, improved solution.
        This mimics meta-cognitive reasoning: solve → evaluate → improve.
        """
        # Step 1: Generate an initial solution using a general-purpose flexible custom approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and solve it methodically.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution — now with guided awareness
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Re-solve the problem while addressing these points. Provide a clear, accurate answer."
        )

        return final_solution