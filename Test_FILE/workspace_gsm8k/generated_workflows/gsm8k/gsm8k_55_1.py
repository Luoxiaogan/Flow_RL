# Workflow ID: gsm8k_55_1
# Benchmark: gsm8k
# Data Indices: [782, 557]

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
        then uses ScEnsemble to select the most consistent and accurate one.
        Finally, it applies a single Review step to polish the selected solution.
        This approach improves robustness by leveraging multiple perspectives
        and reduces reliance on any single reasoning path.
        """

        # Step 1: Generate multiple candidate solutions in parallel via loops
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Direct step-by-step breakdown
                instruction = "Solve the problem by breaking it into small, clear steps. Use basic arithmetic and show all work."
            elif i == 1:
                # Strategy 2: Use visual or concrete analogy (e.g., drawing, real-world comparison)
                instruction = "Explain the problem as if you're teaching a child. Use analogies or physical examples to make it intuitive."
            else:
                # Strategy 3: Start with estimation, then refine
                instruction = "First estimate the answer roughly, then solve precisely. Show how your estimate guides your final calculation."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final polish — review the best solution for clarity, logic, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer