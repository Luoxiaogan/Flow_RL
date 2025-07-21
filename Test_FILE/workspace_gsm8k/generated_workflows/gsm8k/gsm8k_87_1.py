# Workflow ID: gsm8k_87_1
# Benchmark: gsm8k
# Data Indices: [574, 380]

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
        Robust Parallel Ensemble Workflow with Diverse Reasoning Paths.
        Generates 3 distinct solutions using different reasoning strategies via FlexibleCustom,
        then selects the most consistent one using ScEnsemble. Final review ensures clarity and correctness.
        This approach is fundamentally different from the Reflect+Iterative method — it leverages diversity
        to improve accuracy through consensus rather than refinement.
        """

        # Step 1: Generate 3 independent solutions using different reasoning patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (step-by-step)
                solution = await self.flexible_custom(
                    custom_instruction="Solve the problem by following a clear sequence: identify each item, calculate its cost, sum all costs.",
                    reasoning_pattern="sequential",
                    steps=["identify_items", "calculate_individual_costs", "sum_total"]
                )
            elif i == 1:
                # Strategy 2: Parallel calculation (group items first)
                solution = await self.flexible_custom(
                    custom_instruction="Group similar items together (e.g., jackets, shorts, pants), compute total per group, then add groups.",
                    reasoning_pattern="parallel",
                    steps=["group_items", "compute_group_totals", "aggregate_totals"]
                )
            else:
                # Strategy 3: Estimation-first then verification
                solution = await self.flexible_custom(
                    custom_instruction="First estimate the total roughly, then compute exact values. Compare both to check reasonableness.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "calculate_exact", "verify_consistency"],
                    max_iterations=1
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final Review to polish clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer