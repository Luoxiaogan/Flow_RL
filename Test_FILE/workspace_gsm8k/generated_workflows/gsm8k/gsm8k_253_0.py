# Workflow ID: gsm8k_253_0
# Benchmark: gsm8k
# Data Indices: [582, 633]

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
        # Step 1: Generate 3 distinct solutions using different flexible custom patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Approach this as a step-by-step arithmetic word problem.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "set_up_equations", "solve"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Use a visual model or diagram-based approach to solve.",
            reasoning_pattern="branching",
            steps=["draw_diagram", "label_elements", "apply_math_operations", "verify"]
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller sub-problems first.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "subproblem_solving", "combine_results"],
            max_iterations=2
        )

        # Step 2: Ensembling – select the most consistent and accurate solution
        ensemble_input = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=ensemble_input)

        # Step 3: Final Review for polish and clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer