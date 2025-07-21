# Workflow ID: gsm8k_124_0
# Benchmark: gsm8k
# Data Indices: [22, 893]

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
        Diverse and efficient workflow using iterative refinement with FlexibleCustom.
        This pattern is simple yet effective: start with a structured plan, refine it iteratively,
        then optionally review for clarity — all while avoiding unnecessary complexity.
        """
        # Step 1: Use FlexibleCustom in iterative mode to systematically solve the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify"],
            max_iterations=2
        )

        # Step 2: Optionally refine further if needed (simple single review for polish)
        final_solution = await self.review(pre_solution=solution)

        return final_solution