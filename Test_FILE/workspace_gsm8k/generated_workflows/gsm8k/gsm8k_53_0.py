# Workflow ID: gsm8k_53_0
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
        This is a diverse workflow using the Iterative Refinement pattern.
        It starts with a general-purpose flexible custom step, then refines iteratively.
        """
        # Step 1: Generate an initial solution using a sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what needs to be solved and break it into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "compute", "verify"]
        )

        # Step 2: Apply iterative refinement — review twice to improve accuracy
        refined_solution_1 = await self.review(pre_solution=initial_solution)
        final_solution = await self.review(pre_solution=refined_solution_1)

        return final_solution