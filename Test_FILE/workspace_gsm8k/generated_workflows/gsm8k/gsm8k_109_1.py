# Workflow ID: gsm8k_109_1
# Benchmark: gsm8k
# Data Indices: [508, 415, 7]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Robust Parallel Ensemble Workflow with Diverse Reasoning Strategies.
        Generates 3 distinct solutions using varied reasoning patterns (sequential, parallel, iterative),
        then selects the most consistent one via ScEnsemble. Final review ensures clarity and correctness.
        This approach improves reliability by leveraging multiple perspectives — a key strength over single-path methods.
        """
        # Step 1: Generate 3 diverse initial solutions using FlexibleCustom with different patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential: Clear step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into logical steps and solve each systematically.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_unknowns", "formulate_equations", "solve"]
                )
            elif i == 1:
                # Parallel: Consider multiple interpretations simultaneously
                solution = await self.flexible_custom(
                    custom_instruction="Explore alternative approaches to solving this problem.",
                    reasoning_pattern="parallel",
                    steps=["approach_a", "approach_b", "compare_results"]
                )
            else:
                # Iterative: Refine through multiple passes
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine your answer iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer