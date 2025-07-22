# Workflow ID: gsm8k_31_1
# Benchmark: gsm8k
# Data Indices: [396, 926, 650]

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
        It generates three independent solutions in parallel (via loop), then selects the best one.
        This approach increases robustness by leveraging multiple reasoning paths without complex iteration or reflection.
        It's efficient because it avoids redundant refinement steps and directly compares candidate solutions.
        """

        # Step 1: Generate multiple independent solutions using a simple loop
        solution_list = []
        for _ in range(3):  # Three independent attempts with different initial reasoning
            solution = await self.custom(
                instruction="Solve the problem step-by-step. Focus on clarity and logical correctness."
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the set
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution