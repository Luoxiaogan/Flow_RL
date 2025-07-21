# Workflow ID: gsm8k_156_0
# Benchmark: gsm8k
# Data Indices: [935, 614, 155]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Reflect on it to identify potential flaws or improvements.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- Step 1: Generate multiple solutions in parallel ---
        solutions = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step. Break it into clear logical steps. Be precise."
            )
            solutions.append(sol)

        # --- Step 2: Enforce quality by selecting the best solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Critically reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Use reflection to generate a refined solution ---
        # Use FlexibleCustom in iterative mode to apply structured improvement based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: '{reflection}'. Now solve the problem again, focusing on improving clarity, accuracy, and completeness.",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "reformulate_approach", "solve_newly_informed", "verify_again"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution