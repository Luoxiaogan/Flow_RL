# Workflow ID: gsm8k_199_0
# Benchmark: gsm8k
# Data Indices: [321, 262, 23]

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
        Generates 3 independent solutions with varied reasoning strategies via FlexibleCustom,
        then selects the best one using ScEnsemble. Final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential: Break down step-by-step logically
                solution = await self.flexible_custom(
                    custom_instruction="Solve this math problem by identifying each component separately and computing totals systematically.",
                    reasoning_pattern="sequential",
                    steps=["identify_items", "compute_individual_costs", "sum_total"]
                )
            elif i == 1:
                # Iterative: Start with an estimate, refine it
                solution = await self.flexible_custom(
                    custom_instruction="Begin with a rough calculation, then improve accuracy through iterative refinement.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "verify"],
                    max_iterations=2
                )
            else:
                # Branching: Consider multiple paths (e.g., cost per item vs total items)
                solution = await self.flexible_custom(
                    custom_instruction="Explore at least two different approaches to solving the problem and compare results.",
                    reasoning_pattern="branching",
                    steps=["approach_a", "approach_b", "compare_results"]
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the selected answer
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer