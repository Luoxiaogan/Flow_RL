# Workflow ID: gsm8k_285_1
# Benchmark: gsm8k
# Data Indices: [764, 86, 182]

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
        It generates three distinct solutions using different reasoning strategies,
        then selects the most consistent one via ensemble. A final review ensures clarity and correctness.
        This approach is fundamentally different from iterative refinement—it explores multiple paths simultaneously.
        """

        # Step 1: Generate 3 independent solutions using varied instructions to encourage diversity
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this step-by-step using arithmetic operations only—no algebra."
            elif i == 1:
                instruction = "Break the problem into smaller parts and solve each part systematically."
            else:
                instruction = "Use a visual or diagram-based reasoning strategy if applicable; otherwise, apply logical decomposition."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the selected solution—improve clarity, fix minor errors, ensure completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer