# Workflow ID: gsm8k_120_1
# Benchmark: gsm8k
# Data Indices: [906, 125]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it applies a
        single Review step to polish the best solution — ensuring both diversity of thought
        and final quality assurance.
        """
        # Step 1: Generate multiple solutions in parallel using varied instructions
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math problem by first identifying all given units and converting them to a common base before proceeding."
            elif i == 1:
                instruction = "Break the problem into smaller sub-problems, solve each independently, then combine the results logically."
            else:
                instruction = "Use a systematic approach: define variables, write equations, and solve step-by-step without skipping any intermediate calculations."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final refinement using Review to improve clarity, logic flow, or correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution