# Workflow ID: gsm8k_134_0
# Benchmark: gsm8k
# Data Indices: [728, 293, 378]

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
        1. Generate 3 independent solutions via parallel ensemble (robustness).
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on it to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve this math word problem step-by-step by breaking it into clear logical parts.")
            solutions.append(sol)
        
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 3: Conditional Regeneration based on Reflection ---
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
            # If reflection indicates flaws, use flexible custom with iterative pattern to refine
            refined_solution = await self.flexible_custom(
                custom_instruction="Based on the following reflection, re-solve the problem with careful attention to any missed steps or assumptions.",
                previous_results=[best_solution, reflection],
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "rethink_approach", "refine_solution"],
                max_iterations=2
            )
            return refined_solution
        else:
            # If no major issues found, return the original best solution
            return best_solution