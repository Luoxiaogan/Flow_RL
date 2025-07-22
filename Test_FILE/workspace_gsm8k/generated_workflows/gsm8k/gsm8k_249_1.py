# Workflow ID: gsm8k_249_1
# Benchmark: gsm8k
# Data Indices: [965, 242]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and applies the Review operator twice
        to progressively improve the solution through structured feedback loops.
        This approach emphasizes stepwise enhancement rather than reflection-based regeneration.
        """
        # Step 1: Generate a basic solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem in clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: First refinement — review the initial solution for clarity, logic, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review to address remaining issues
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution