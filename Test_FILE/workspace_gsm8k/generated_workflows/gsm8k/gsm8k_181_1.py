# Workflow ID: gsm8k_181_1
# Benchmark: gsm8k
# Data Indices: [765, 126]

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
        Iterative Refinement with Meta-Cognitive Reflection: 
        Generate an initial solution, then use reflection to guide iterative improvements.
        This structure introduces a meta-cognitive loop where each refinement is informed by critical analysis of the previous attempt — fundamentally different from simple back-to-back reviews.
        """
        # Step 1: Generate an initial solution using clear, structured reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly and concisely."
        )

        # Step 2: Reflect on the initial solution — identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a second, improved solution via Custom
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again with deeper insight and corrected assumptions."
        )

        # Step 4: Review the improved solution to polish it further
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution