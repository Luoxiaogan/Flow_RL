# Workflow ID: gsm8k_23_0
# Benchmark: gsm8k
# Data Indices: [468, 197, 853]

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
        Step 1: Generate multiple solutions via parallel ensemble (3 attempts).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on the selected solution to uncover hidden assumptions or errors.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- PARALLEL ENSEMBLE: Generate 3 independent solutions ---
        solutions = []
        for _ in range(3):
            solution = await self.custom(instruction="Solve the problem step-by-step. Break it into parts: identify knowns, unknowns, and apply logical reasoning.")
            solutions.append(solution)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT: Critically analyze the best solution without rewriting it ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- CONDITIONAL LOGIC BASED ON REFLECTION ---
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            # If reflection indicates flaws, regenerate using iterative flexible custom
            refined_solution = await self.flexible_custom(
                custom_instruction="Re-solve the problem based on this reflection: " + reflection,
                reasoning_pattern="iterative",
                steps=["re-analyze", "adjust_assumptions", "recalculate"],
                max_iterations=2,
                use_structured_output=True
            )
            return refined_solution
        else:
            # If no major issues found, return the best solution as-is
            return best_solution