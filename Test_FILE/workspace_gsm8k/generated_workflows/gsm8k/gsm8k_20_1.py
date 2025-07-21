# Workflow ID: gsm8k_20_1
# Benchmark: gsm8k
# Data Indices: [606, 241]

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
        Robust parallel ensemble workflow with diverse reasoning strategies.
        Generates 3 distinct solutions using different FlexibleCustom patterns,
        then selects the best one via ScEnsemble. Final review ensures clarity and correctness.
        This approach is fundamentally different from iterative refinement — it explores multiple paths simultaneously.
        """
        # Step 1: Generate 3 independent solutions using different reasoning patterns
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: step-by-step breakdown
                solution = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "formulate_plan", "execute_calculation", "validate"],
                    custom_instruction="Break down the problem logically and solve step by step."
                )
            elif i == 1:
                # Parallel reasoning: consider multiple interpretations or methods
                solution = await self.flexible_custom(
                    reasoning_pattern="parallel",
                    steps=["analyze_alternatives", "compare_approaches", "select_best"],
                    custom_instruction="Explore at least two different ways to interpret and solve this problem."
                )
            else:
                # Iterative refinement (but used here as a third distinct style)
                solution = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "finalize"],
                    max_iterations=2,
                    custom_instruction="Start with an estimate, then improve it through logical steps."
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish and ensure no critical errors remain
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer