# Workflow ID: gsm8k_224_1
# Benchmark: gsm8k
# Data Indices: [169, 651]

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
        Diverse and efficient workflow using Iterative Refinement with a single FlexibleCustom in iterative mode.
        This approach starts with an initial attempt, then progressively refines it through 2 iterations.
        It's simpler than the existing workflow but still leverages multiple reasoning passes for improvement.
        """

        # --- Step 1: Initial Solution via Iterative FlexibleCustom (first pass) ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving the problem step-by-step.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=1
        )

        # --- Step 2: Refine Using Same FlexibleCustom (second pass) ---
        refined_solution = await self.flexible_custom(
            custom_instruction="Improve the solution by addressing potential gaps or errors.",
            reasoning_pattern="iterative",
            steps=["review_previous", "refine", "reverify"],
            max_iterations=2,
            previous_results=[initial_solution]
        )

        # --- Step 3: Final Review for polish (optional but effective for clarity) ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer