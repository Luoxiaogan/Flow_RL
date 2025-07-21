# Workflow ID: gsm8k_88_1
# Benchmark: gsm8k
# Data Indices: [522, 208]

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
        Robust parallel ensemble workflow using three diverse reasoning strategies.
        This approach generates multiple candidate solutions via different patterns,
        then selects the most consistent one using ScEnsemble. Final review ensures clarity.
        """
        # Step 1: Generate 3 independent solutions using different FlexibleCustom configurations
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential reasoning with explicit steps
                solution = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_variables", "set_up_equation", "solve"],
                    custom_instruction="Solve step-by-step by identifying knowns, defining variables, setting up equations, and solving."
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (like a loop)
                solution = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "check_consistency", "adjust"],
                    max_iterations=2,
                    custom_instruction="Start with an initial guess, check consistency, and adjust iteratively."
                )
            else:
                # Strategy 3: Branching logic to explore alternatives
                solution = await self.flexible_custom(
                    reasoning_pattern="branching",
                    steps=["consider_case_a", "consider_case_b", "compare_outcomes"],
                    custom_instruction="Explore multiple cases or interpretations of the problem and compare outcomes."
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the selected answer for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer