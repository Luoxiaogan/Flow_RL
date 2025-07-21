# Workflow ID: gsm8k_28_1
# Benchmark: gsm8k
# Data Indices: [126, 326]

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
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. A final review ensures clarity
        and correctness — enhancing robustness against reasoning errors or misinterpretations.
        """
        # Step 1: Generate multiple diverse solutions in parallel using FlexibleCustom with different patterns
        solution_list = []
        for i in range(3):
            # Use different reasoning patterns to encourage diversity
            if i == 0:
                solution = await self.flexible_custom(
                    custom_instruction="Solve by identifying all given quantities first, then applying arithmetic operations step-by-step.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "set_up_operations", "calculate", "verify"]
                )
            elif i == 1:
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into parts: what was given away, what remains, and how to compute totals.",
                    reasoning_pattern="branching",
                    steps=["analyze_giveaways", "compute_remaining", "summarize"]
                )
            else:
                solution = await self.flexible_custom(
                    custom_instruction="Start with estimation, then refine calculations based on exact values.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "finalize"],
                    max_iterations=2
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish and clarify the chosen solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer