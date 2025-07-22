# Workflow ID: gsm8k_288_1
# Benchmark: gsm8k
# Data Indices: [6, 804, 830]

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
        It generates multiple independent solutions in parallel (via a loop), then selects the best one.
        This approach is efficient because it avoids over-reliance on a single reasoning path,
        while still being simple — just two steps: generate 3 solutions, pick the best.
        """
        # Step 1: Generate 3 different solutions using Custom with varied instructions
        solutions = []
        for i in range(3):
            instruction = f"Attempt {i+1}: Solve the problem step-by-step, explaining each part clearly."
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution