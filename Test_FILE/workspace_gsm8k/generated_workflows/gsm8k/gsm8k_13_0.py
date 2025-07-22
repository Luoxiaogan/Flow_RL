# Workflow ID: gsm8k_13_0
# Benchmark: gsm8k
# Data Indices: [739, 649, 62]

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
        This is a diverse and efficient workflow using iterative refinement with FlexibleCustom.
        It uses a structured, step-by-step reasoning pattern to solve the problem logically.
        The flexibility of FlexibleCustom allows for clear, modular reasoning without overcomplication.
        """
        # Use FlexibleCustom in sequential mode to break down the problem systematically
        solution = await self.flexible_custom(
            custom_instruction="Solve this math word problem by following these steps: analyze the question, identify known values, set up equations, compute the result, and verify the answer.",
            reasoning_pattern="sequential",
            steps=["analyze", "identify_knowns", "set_up_equations", "compute", "verify"]
        )
        
        # Optional: One round of review to polish the final output
        final_solution = await self.review(pre_solution=solution)
        
        return final_solution