# Workflow ID: gsm8k_75_1
# Benchmark: gsm8k
# Data Indices: [756, 204]

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
        then selects the most consistent one via ScEnsemble. A final review ensures clarity and correctness.
        This approach enhances robustness by leveraging multiple perspectives and reducing reliance on a single flawed path.
        """
        # Step 1: Generate 3 independent solutions using FlexibleCustom with different reasoning patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to break down the problem into clear steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "set_up_equations", "solve"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Apply iterative refinement starting from an estimate and improving it step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "check_consistency", "refine"],
            max_iterations=2
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Use branching logic to explore alternative interpretations of the problem before settling on a path.",
            reasoning_pattern="branching",
            steps=["analyze_assumptions", "explore_options", "choose_best_path", "validate"]
        )

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and logical coherence
        ensemble_result = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Final Review to polish the selected solution for clarity and correctness
        final_solution = await self.review(pre_solution=ensemble_result)

        return final_solution