# Workflow ID: gsm8k_127_0
# Benchmark: gsm8k
# Data Indices: [100, 98]

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
        It generates 3 independent solutions with varied reasoning strategies,
        then selects the best one via ensemble, followed by a final review for refinement.
        """
        # --- Step 1: Generate multiple solutions in parallel using different strategies ---
        solution_list = []
        strategies = [
            "Break the problem into clear steps: identify knowns, unknowns, and apply relevant formulas.",
            "Use a systematic approach: define variables, write equations, solve step-by-step.",
            "Think like a teacher: explain each part of the solution as if instructing a student."
        ]

        for i in range(3):
            solution = await self.custom(instruction=strategies[i])
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final review to improve clarity and correctness ---
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution