# Workflow ID: gsm8k_365_0
# Benchmark: gsm8k
# Data Indices: [347, 77, 465]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates 3 different solutions via varied reasoning strategies, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Use a step-by-step decomposition approach.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Apply a parallel thinking strategy — consider multiple interpretations.",
            reasoning_pattern="parallel",
            steps=["interpret", "evaluate_options", "select_best", "refine"]
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Use iterative refinement to improve accuracy over time.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "check_for_errors", "improve"],
            max_iterations=2
        )

        # Step 2: Ensemple the three solutions to pick the most consistent and accurate one
        ensemble_solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        # Step 3: Final Review for polish and clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer