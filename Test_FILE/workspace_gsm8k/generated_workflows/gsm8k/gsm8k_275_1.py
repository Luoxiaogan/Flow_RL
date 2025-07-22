# Workflow ID: gsm8k_275_1
# Benchmark: gsm8k
# Data Indices: [332, 831]

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
        This is a diverse and efficient workflow using Iterative Refinement + Reflect-and-Regenerate.
        Step 1: Generate an initial solution using a structured approach via FlexibleCustom (sequential).
        Step 2: Use the Reflect operator to critique the solution for hidden assumptions or logical gaps.
        Step 3: If reflection indicates issues, use a second FlexibleCustom call with iterative refinement to improve it.
        Step 4: Otherwise, return the initial solution — no unnecessary steps.
        
        Key difference from existing: Uses Reflect + Iterative FlexibleCustom as a conditional refinement loop instead of parallel ensemble. More efficient, less redundant computation.
        """

        # --- Step 1: Initial Solution via Structured Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "identify_knowns", "apply_math", "compute_final"]
        )

        # --- Step 2: Reflect on the Solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Conditional Regeneration Based on Reflection ---
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            # Only refine if reflection reveals flaws — avoids unnecessary work
            improved_solution = await self.flexible_custom(
                custom_instruction=f"Improve the solution based on this reflection: {reflection}",
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_logic", "recompute"],
                max_iterations=2
            )
            return improved_solution
        else:
            # No issues found — return clean, initial solution
            return initial_solution