# Workflow ID: gsm8k_72_1
# Benchmark: gsm8k
# Data Indices: [255, 596, 31]

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
        Reflect and Regenerate Workflow: 
        1. Generate an initial solution.
        2. Critically reflect on it to identify potential flaws or improvements.
        3. Use that reflection to guide a new, improved solution.
        This mimics meta-cognitive reasoning — evaluating one's own thinking before acting again.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. Explain each step clearly."
        )

        # Step 2: Reflect on the initial solution — identify assumptions, logic gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a refined, more robust solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses the issues identified in the reflection."
        )

        return final_solution