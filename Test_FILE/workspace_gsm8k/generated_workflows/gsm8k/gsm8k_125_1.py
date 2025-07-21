# Workflow ID: gsm8k_125_1
# Benchmark: gsm8k
# Data Indices: [548, 856]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel approach (fan-out).
        2. Use ScEnsemble to pick the best one.
        3. Reflect on that solution to uncover hidden flaws or assumptions.
        4. Regenerate a final solution guided by reflection — this is a meta-cognitive loop.
        
        This design avoids iterative refinement in favor of diverse initial reasoning paths,
        followed by critical analysis and targeted improvement — more robust than single-path approaches.
        """
        # Step 1: Generate multiple independent solutions using FlexibleCustom in parallel mode
        solution_pool = []
        for i in range(3):
            solution = await self.flexible_custom(
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve"],
                custom_instruction="Solve the problem from a unique perspective each time — e.g., step-by-step, visual, or formulaic."
            )
            solution_pool.append(solution)

        # Step 2: Select the best among them using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the selected solution — no rewriting yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution:\n{reflection}\n\nUse this insight to generate a revised, more accurate answer. Focus on clarity, correctness, and completeness."
        )

        return final_answer