# Workflow ID: gsm8k_54_0
# Benchmark: gsm8k
# Data Indices: [789, 646, 521]

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
        It leverages the "Iterative Refinement" pattern but enhances it with structured reasoning steps.
        The flexibility of FlexibleCustom allows for step-by-step improvement without hardcoding logic.
        """
        # Step 1: Use FlexibleCustom in iterative mode to build a solution through progressive refinement
        solution = await self.flexible_custom(
            custom_instruction="Solve this math word problem systematically.",
            reasoning_pattern="iterative",
            steps=["understand_problem", "identify_knowns", "formulate_plan", "compute_solution", "verify_answer"],
            max_iterations=2
        )

        # Step 2: Reflect on the solution to uncover potential flaws or assumptions
        reflection = await self.reflect(pre_solution=solution)

        # Step 3: Use the reflection to guide a final custom refinement — this is a meta-cognitive loop
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Provide a revised, improved solution that addresses any weaknesses."
        )

        return final_solution