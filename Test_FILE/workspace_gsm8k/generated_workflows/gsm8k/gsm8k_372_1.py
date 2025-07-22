# Workflow ID: gsm8k_372_1
# Benchmark: gsm8k
# Data Indices: [120, 577, 875]

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
        This is a diverse and robust workflow that uses:
        1. Parallel Ensemble with varied reasoning strategies (different custom instructions)
        2. A branching logic based on reflection to decide whether to refine or accept
        3. Iterative refinement only if the reflection suggests improvement is needed
        4. Uses FlexibleCustom in "parallel" mode for one of the solutions to add diversity
        """

        # Step 1: Generate 3 independent solutions using different reasoning styles
        solution_pool = []

        # Solution 1: Direct step-by-step breakdown
        sol1 = await self.custom(
            instruction="Solve the problem by breaking it into clear, sequential steps. Show all calculations explicitly."
        )
        solution_pool.append(sol1)

        # Solution 2: Use FlexibleCustom in parallel mode — this simulates multiple paths simultaneously
        sol2 = await self.flexible_custom(
            custom_instruction="Apply structured problem-solving: identify knowns, unknowns, formulas, then compute.",
            reasoning_pattern="parallel",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify"]
        )
        solution_pool.append(sol2)

        # Solution 3: Use a creative approach — encourage thinking like a teacher explaining to a student
        sol3 = await self.custom(
            instruction="Explain your solution as if you're teaching a middle schooler — use simple language, analogies, and check each step."
        )
        solution_pool.append(sol3)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically — ask what could be wrong or missing in the best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Branch logic: If reflection indicates potential issues, do iterative refinement.
        # Otherwise, return the best solution directly.
        if "error" in reflection.lower() or "missed" in reflection.lower() or "assumption" in reflection.lower():
            final_solution = best_solution
            for _ in range(2):  # Two rounds of review for polish
                revised = await self.review(pre_solution=final_solution)
                final_solution = revised
        else:
            final_solution = best_solution

        return final_solution