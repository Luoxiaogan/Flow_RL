# Workflow ID: gsm8k_155_1
# Benchmark: gsm8k
# Data Indices: [840, 613, 842]

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
        1. Generate 3 independent solutions using parallel reasoning (fan-out).
        2. Use ScEnsemble to select the best candidate.
        3. Reflect critically on that solution to uncover hidden assumptions or errors.
        4. Regenerate a final answer informed by the reflection — mimicking meta-cognition.
        
        This combines robustness (parallel) with deep introspection (reflect), creating a more accurate and thoughtful outcome than either alone.
        """
        # Step 1: Generate multiple diverse solutions via parallel ensemble
        solution_pool = []
        for i in range(3):
            instruction = (
                "Solve this problem using a different approach each time: "
                "First, try breaking it into parts. Second, use direct calculation. Third, simulate the scenario step-by-step."
            )
            solution = await self.custom(instruction=instruction)
            solution_pool.append(solution)

        # Step 2: Select the strongest solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the selected solution without rewriting
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        final_instruction = (
            f"Given the following initial solution:\n{best_solution}\n\n"
            f"And the following reflection on potential flaws or improvements:\n{reflection}\n\n"
            "Now, provide a revised and improved solution based on these insights."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer