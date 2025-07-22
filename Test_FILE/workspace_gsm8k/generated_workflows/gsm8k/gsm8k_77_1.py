# Workflow ID: gsm8k_77_1
# Benchmark: gsm8k
# Data Indices: [48, 213, 106]

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
        This is a diverse workflow using the Reflect-and-Regenerate pattern with iterative refinement.
        It starts with an initial solution, then uses 'Reflect' to critique it, and finally generates a refined solution based on that reflection.
        The structure introduces meta-cognition: the model reflects on its own reasoning before improving it — a fundamentally different logic than simple sequential review.
        """
        # Step 1: Generate an initial solution using a flexible custom approach with structured steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically. Identify knowns, unknowns, and relationships.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Use the new 'Reflect' operator to critically assess the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final solution informed by the reflection — this is the core of the novel logic
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. Now, solve the problem again, focusing on addressing these points. Be precise and logical."
        )

        return final_solution