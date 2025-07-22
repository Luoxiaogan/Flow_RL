# Workflow ID: gsm8k_214_1
# Benchmark: gsm8k
# Data Indices: [38, 899]

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
        It generates 3 independent solutions with different reasoning strategies,
        then selects the most consistent one using ScEnsemble. Finally, it reviews
        the selected solution to ensure clarity and correctness — ensuring robustness
        through diversity and meta-cognition.
        """
        # Step 1: Generate multiple candidate solutions using varied approaches
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Break the problem into clear, logical steps and solve each step sequentially."
            elif i == 1:
                instruction = "Use a visual or diagrammatic approach to model the problem before solving."
            else:
                instruction = "Start with an estimate, then refine your answer using precise calculations."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish and clarify the chosen solution
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution