# Workflow ID: gsm8k_30_1
# Benchmark: gsm8k
# Data Indices: [503, 938, 854]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        1. Generate 3 independent solutions using parallel reasoning (Fan-out).
        2. Use ScEnsemble to select the best one.
        3. Reflect on the selected solution to uncover hidden assumptions or flaws.
        4. Regenerate a final solution informed by the reflection — this mimics human meta-cognition.
        This approach combines robustness (from ensembling) with deep critical thinking (from reflection), avoiding over-reliance on any single path.
        """
        # Step 1: Generate 3 diverse initial solutions via parallel reasoning
        solutions = []
        for i in range(3):
            instruction = f"Solution {i+1}: Solve the problem step-by-step using a unique method. Focus on clarity and logical progression."
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # Step 2: Select the strongest solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        final_instruction = (
            "Given the following reflection on the initial solution, "
            "provide a revised answer that addresses potential flaws or missed insights: "
            f"{reflection}"
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution