# Workflow ID: gsm8k_321_1
# Benchmark: gsm8k
# Data Indices: [641, 481]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three distinct solutions using different reasoning strategies (sequential, iterative, branching),
        then uses ScEnsemble to select the most consistent and accurate one. Finally, it applies a single Review
        for final polish — ensuring robustness through diversity of thought and consensus-based selection.
        """
        # Step 1: Generate multiple independent solutions using FlexibleCustom with varied patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Solve this step-by-step using a clear sequential approach.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Begin with an estimation, then refine your answer in multiple passes.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations or paths to the solution.",
            reasoning_pattern="branching",
            steps=["identify_assumptions", "explore_paths", "select_best_path", "calculate"]
        )

        # Step 2: Use ScEnsemble to evaluate and select the best solution from the three
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Final review to catch any remaining issues or ambiguities
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer