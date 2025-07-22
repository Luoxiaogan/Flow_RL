# Workflow ID: gsm8k_255_0
# Benchmark: gsm8k
# Data Indices: [551, 93, 450]

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
        This is a diverse and efficient workflow using iterative refinement with flexible custom reasoning.
        It uses the 'iterative' pattern in FlexibleCustom to progressively improve a solution,
        avoiding unnecessary complexity while ensuring robustness through structured iteration.
        """
        # Step 1: Use iterative FlexibleCustom to generate a solution in multiple passes
        # The reasoning pattern ensures systematic improvement without hardcoding steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving the problem step-by-step.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Review the result to catch any remaining errors or ambiguities
        final_solution = await self.review(pre_solution=initial_solution)

        return final_solution