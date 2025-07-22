# Workflow ID: gsm8k_130_0
# Benchmark: gsm8k
# Data Indices: [511, 722]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple solutions in parallel (fan-out).
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect on it to uncover hidden flaws or assumptions.
        Step 4: Use that reflection to guide a targeted regen (via FlexibleCustom with branching logic).
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_candidates = []
        for i in range(3):  # Generate 3 independent solutions
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into logical steps. Consider all possible interpretations of ambiguous terms."
            )
            solution_candidates.append(candidate)

        # --- SCENSEMBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT (Meta-cognitive critique) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- CONDITIONAL REGENERATION BASED ON REFLECTION ---
        if "assumption" in reflection.lower() or "ambiguity" in reflection.lower():
            # If reflection indicates flawed reasoning, use flexible custom with branching pattern
            final_answer = await self.flexible_custom(
                custom_instruction="Re-solve the problem using a structured approach. First, identify all assumptions made in the previous solution. Then, correct them and proceed step-by-step.",
                previous_results=[best_solution, reflection],
                reasoning_pattern="branching",
                steps=["identify_assumptions", "correct_assumptions", "recompute"]
            )
        else:
            # If no major issues found, refine using Review
            final_answer = await self.review(pre_solution=best_solution)

        return final_answer