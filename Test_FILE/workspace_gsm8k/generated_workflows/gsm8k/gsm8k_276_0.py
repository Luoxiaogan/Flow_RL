# Workflow ID: gsm8k_276_0
# Benchmark: gsm8k
# Data Indices: [897, 466, 979]

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
        Three different solution strategies are generated in parallel, then the best one is selected.
        A final review ensures clarity and correctness.
        """

        # Generate 3 diverse solutions using different reasoning approaches
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Break down the problem into clear steps, label each step logically, and solve it methodically."
            elif i == 1:
                instruction = "Solve by identifying all quantities, setting up equations or expressions, and computing them in order."
            else:
                instruction = "Think like a teacher: explain the solution as if to someone learning this for the first time."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final refinement via Review to improve clarity and correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution