# Workflow ID: gsm8k_193_1
# Benchmark: gsm8k
# Data Indices: [732, 800, 701]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent and accurate one.
        Finally, it performs a single review pass for polish and clarity — 
        ensuring robustness through diversity and consensus.
        """
        # Step 1: Generate multiple solutions in parallel using varied strategies
        solution_list = []
        strategies = [
            "Solve step-by-step by identifying each item's cost and summing them up.",
            "Break the problem into parts: cars, paint, brushes. Calculate each separately before adding.",
            "Use a structured approach: define variables (e.g., total_cost = car_cost + paint_cost + brush_cost), then compute."
        ]

        for instruction in strategies:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ensemble to pick the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via review to improve clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer