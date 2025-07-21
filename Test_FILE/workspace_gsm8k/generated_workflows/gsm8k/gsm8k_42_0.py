# Workflow ID: gsm8k_42_0
# Benchmark: gsm8k
# Data Indices: [933, 697, 25]

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
        Diverse and robust workflow using Parallel Ensemble with iterative refinement.
        Generates 3 different solutions via FlexibleCustom with varied reasoning patterns,
        then ensembles them, and finally reviews the best result for consistency.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Apply a systematic step-by-step breakdown.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        
        solution2 = await self.flexible_custom(
            custom_instruction="Use a parallel approach to explore multiple interpretations.",
            reasoning_pattern="parallel",
            steps=["identify_assumptions", "evaluate_options", "select_best", "compute"]
        )
        
        solution3 = await self.flexible_custom(
            custom_instruction="Refine iteratively starting from an initial estimate.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )

        # Step 2: Ensembling - select the most consistent solution
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to catch any remaining errors or ambiguities
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer