# Workflow ID: gsm8k_173_0
# Benchmark: gsm8k
# Data Indices: [239, 39, 322]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect + Regenerate pattern to refine the best solution using meta-cognition
        """
        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_pool = []
        for i in range(3):  # Generate 3 different approaches
            instruction = "Solve the problem by breaking it into logical steps. Focus on clarity and correctness."
            sol = await self.custom(instruction=instruction)
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the most promising solution
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the chosen solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, regenerate a new improved solution
        # The reflection guides the next step—this mimics human metacognition
        improved_instruction = f"Given the following reflection on the previous solution: '{reflection}'. Now, produce a revised solution that addresses potential weaknesses or missed assumptions."
        final_solution = await self.custom(instruction=improved_instruction)

        return final_solution