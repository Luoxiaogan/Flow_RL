# Workflow ID: gsm8k_98_1
# Benchmark: gsm8k
# Data Indices: [319, 317, 145]

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
        - First, generate 3 independent solutions using FlexibleCustom with different reasoning patterns.
        - Use ScEnsemble to select the best one.
        - Critically reflect on that winner to uncover hidden assumptions or errors.
        - Finally, regenerate a refined solution informed by the reflection — mimicking human meta-cognition.
        
        This approach combines robustness (parallel exploration) with deep introspection (reflection), 
        ensuring both breadth and depth in reasoning while avoiding over-reliance on any single path.
        """
        # Step 1: Generate 3 diverse solutions via parallel ensemble
        solution_pool = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem logically, breaking it into clear steps.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_pool.append(solution)

        # Step 2: Select the best solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the selected solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution based on reflection insights
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Use this insight to produce a corrected and improved answer."
        )

        return final_answer