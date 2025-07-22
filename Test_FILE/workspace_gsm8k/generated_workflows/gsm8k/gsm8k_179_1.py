# Workflow ID: gsm8k_179_1
# Benchmark: gsm8k
# Data Indices: [639, 837, 27]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 independently reasoned solutions via different FlexibleCustom patterns,
        then selects the most consistent one via ScEnsemble. Final review ensures clarity.
        This structure improves reliability by leveraging multiple reasoning paths.
        """

        # Step 1: Generate 3 distinct solutions using different reasoning patterns
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential approach: clear step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve the problem systematically.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative approach: refine through passes
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Branching approach: explore alternative interpretations
                solution = await self.flexible_custom(
                    custom_instruction="Consider multiple valid interpretations of the problem.",
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "explore_paths", "choose_best"]
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer