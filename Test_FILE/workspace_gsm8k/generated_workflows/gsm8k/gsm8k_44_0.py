# Workflow ID: gsm8k_44_0
# Benchmark: gsm8k
# Data Indices: [914, 391, 406]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It starts with a flexible custom approach to structure reasoning, then uses reflection
        to critique the result before finalizing — all in under 6 steps for maximum efficiency.
        """
        # Step 1: Use FlexibleCustom in "iterative" mode to generate an initial structured solution
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Break the problem into clear steps: identify knowns, unknowns, apply logic, and verify."
        )

        # Step 2: Reflect on the initial solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final improved solution based on reflection
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Use this insight to produce a precise, well-structured answer without redundancy."
        )

        return final_solution