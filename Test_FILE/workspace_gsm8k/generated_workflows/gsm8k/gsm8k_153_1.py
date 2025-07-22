# Workflow ID: gsm8k_153_1
# Benchmark: gsm8k
# Data Indices: [794, 411]

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
        This is a diverse and efficient workflow using the Parallel Ensemble + Reflect-and-Regenerate hybrid pattern.
        It generates multiple independent solutions (parallel), then selects the best one for reflection,
        which is used to guide a final refined solution — ensuring both robustness and meta-cognitive improvement.
        """
        # Step 1: Generate three distinct initial solutions via parallel reasoning
        solutions = []
        for i in range(3):
            instruction = f"Generate a unique approach to solving this problem. Focus on clarity and logical structure."
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the strongest candidate from the parallel attempts
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, targeted custom generation for final accuracy
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, provide a corrected and improved solution that addresses potential flaws identified above."
        )

        return final_answer