# Workflow ID: gsm8k_302_1
# Benchmark: gsm8k
# Data Indices: [498, 555]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three distinct solutions using different reasoning strategies,
        then selects the most consistent one via ensemble. Finally, it applies a
        single review to polish the best solution — ensuring robustness through diversity
        and final refinement.
        """
        # Step 1: Generate multiple independent solutions using varied instructions
        # Each uses a different approach to avoid redundancy and increase coverage
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math problem by first identifying all variables and relationships, then setting up equations step-by-step."
            elif i == 1:
                instruction = "Break down the problem into smaller parts, solve each part independently, and combine the results logically."
            else:
                instruction = "Use a visual or diagrammatic approach (even if abstract) to model the problem before solving numerically."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Apply a final review to improve clarity, correctness, and completeness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution