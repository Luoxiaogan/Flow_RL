# Workflow ID: gsm8k_367_1
# Benchmark: gsm8k
# Data Indices: [556, 220, 839]

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
        Parallel Ensemble + Final Review: Generate three diverse solutions using different reasoning strategies,
        then use ScEnsemble to select the most consistent one. A final review ensures clarity and correctness.
        This pattern improves robustness by leveraging multiple approaches and filtering out inconsistencies.
        """

        # Step 1: Generate 3 independent solutions using varied custom instructions
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step, starting with identifying all quantities and operations involved."
            elif i == 1:
                instruction = "Break the problem into logical phases: initial state, changes, and final outcome. Solve each phase separately."
            else:
                instruction = "Assume a variable for unknowns, write equations based on the scenario, and solve algebraically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement — apply a single round of Review to polish the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer