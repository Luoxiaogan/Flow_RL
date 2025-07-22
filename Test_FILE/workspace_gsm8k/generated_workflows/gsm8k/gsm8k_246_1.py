# Workflow ID: gsm8k_246_1
# Benchmark: gsm8k
# Data Indices: [304, 675, 939]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern with FlexibleCustom.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution, then refine it over two passes.
        Step 2: After refinement, apply a final Review step to polish the answer before returning.
        This approach avoids parallel computation for simplicity while ensuring robustness through structured iteration.
        """

        # --- STEP 1: Use iterative FlexibleCustom for systematic refinement ---
        refined_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate and improve it in each iteration.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "refine", "verify"],
            max_iterations=2
        )

        # --- STEP 2: Final polishing via Review to ensure clarity and correctness ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer