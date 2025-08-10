# Workflow ID: test_GSM8k_7429
# Benchmark: GSM8k
# Data Indices: [7429]

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
        This is a workflow graph using the Parallel Ensemble pattern.
        Generates 3 different solutions with varied instructions, then ensembles them.
        """
        solution_list = []

        # Generate 3 different solutions using varied custom instructions
        for i in range(3):
            instruction = f"Solve the problem step-by-step. Approach {i+1}: Use a unique method to reach the solution."
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Use ScEnsemble to select the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Optional: Review the best solution for refinement
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution