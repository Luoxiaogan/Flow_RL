# Benchmark: GSM8K
# Workflow ID: gsm8k_1
# Data Indices: [40, 41, 42]
# Generation Time: 2025-07-17 22:42:05
# Status: generated
# ==================================================

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

    async def run_workflow(self):
        """
        This is a robust workflow using the Parallel Ensemble pattern.
        It generates three different solutions with varied instructions,
        then selects the best one using ScEnsemble.
        """
        solution_list = []

        # Generate 3 different solutions with distinct reasoning approaches
        for i in range(3):
            instruction = f"Solve the problem step-by-step. Approach {i+1}: Focus on identifying and translating all given relationships."
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Use ScEnsemble to select the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Optional: Review the best solution for refinement
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution