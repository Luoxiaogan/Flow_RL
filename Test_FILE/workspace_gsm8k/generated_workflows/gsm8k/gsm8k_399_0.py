# Workflow ID: gsm8k_399_0
# Benchmark: gsm8k
# Data Indices: [693]

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
        Generates 3 distinct solutions via varied reasoning strategies, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple independent solutions using different approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Direct algebraic approach
                instruction = "Solve step-by-step by setting up an equation based on the relationship between the two quantities."
            elif i == 1:
                # Strategy 2: Step-by-step logical breakdown
                instruction = "Break down the problem into clear steps: identify knowns, unknowns, and how they relate. Then compute the total."
            else:
                # Strategy 3: Use estimation + verification
                instruction = "First estimate the answer logically, then verify your result using reverse calculation."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Enforce consistency with ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via Review for polish and clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer