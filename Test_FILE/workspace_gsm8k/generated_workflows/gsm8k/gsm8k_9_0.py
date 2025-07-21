# Workflow ID: gsm8k_9_0
# Benchmark: gsm8k
# Data Indices: [453, 461, 211]

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
        2. Reflect-and-Regenerate pattern: critique the best solution and rebuild from reflection
        3. Iterative refinement via FlexibleCustom with structured steps for final polish
        """

        # Step 1: Generate 3 independent solutions using parallel ensemble approach
        solution_pool = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve this math word problem by breaking it into clear steps and justifying each step.")
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the best among them
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution — identify potential flaws or missed opportunities
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, regenerate a new solution using Custom with guidance
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem now, incorporating these insights to avoid similar issues."
        )

        # Step 5: Apply iterative refinement using FlexibleCustom to polish the final answer
        final_refined = await self.flexible_custom(
            custom_instruction="Apply an iterative improvement strategy: first analyze assumptions, then validate logic, then finalize.",
            reasoning_pattern="iterative",
            steps=["analyze", "validate", "refine"],
            max_iterations=2
        )

        return final_refined