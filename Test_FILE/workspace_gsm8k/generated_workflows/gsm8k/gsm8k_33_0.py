# Workflow ID: gsm8k_33_0
# Benchmark: gsm8k
# Data Indices: [680, 844]

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
        This is a diverse and iterative refinement-based workflow.
        It starts with an initial solution, then applies Review twice to progressively improve it.
        Uses FlexibleCustom in sequential mode for the first step to ensure structured reasoning.
        """
        # Step 1: Generate an initial structured solution using FlexibleCustom (Sequential pattern)
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps: identify knowns, unknowns, apply operations, verify result.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )

        # Step 2: First review pass — refine clarity and correctness
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # Step 3: Second review pass — focus on completeness and potential oversights
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        # Step 4: Final output — return the iteratively improved solution
        return refined_solution_2