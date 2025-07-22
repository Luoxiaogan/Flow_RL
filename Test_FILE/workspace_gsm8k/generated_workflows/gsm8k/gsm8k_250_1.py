# Workflow ID: gsm8k_250_1
# Benchmark: gsm8k
# Data Indices: [156, 76, 183]

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
        It generates three independent solutions with varied reasoning strategies (sequential, iterative, branching),
        then uses ScEnsemble to select the most consistent one. Finally, it applies a review for final polish.
        This approach enhances robustness by leveraging multiple reasoning paths — a fundamentally different logic from the Reflect-and-Regenerate pattern.
        """

        # Step 1: Generate 3 distinct solutions using FlexibleCustom with different reasoning patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Solve this step-by-step using a sequential approach.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "calculate", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Use an iterative method: start with an estimate, refine twice, then finalize.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "finalize"],
            max_iterations=2
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Apply a branching strategy: consider multiple interpretations of the problem before solving.",
            reasoning_pattern="branching",
            steps=["identify_assumptions", "explore_branches", "choose_best_path", "solve"]
        )

        # Step 2: Use ScEnsemble to pick the best among the three
        ensemble_result = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Final refinement via Review to ensure clarity and correctness
        final_solution = await self.review(pre_solution=ensemble_result)

        return final_solution