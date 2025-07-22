# Workflow ID: gsm8k_230_1
# Benchmark: gsm8k
# Data Indices: [915, 299]

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
        Diverse and efficient workflow using Iterative Refinement + Reflect-and-Regenerate.
        1. Generate an initial solution with a clear step-by-step instruction.
        2. Use Review to improve it once — this is fast and effective for most problems.
        3. If the review process reveals ambiguity or flaw (via Reflect), regenerate with targeted reasoning via FlexibleCustom in iterative mode.
        This avoids unnecessary parallelism while still allowing intelligent refinement when needed.
        """
        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each reasoning step clearly and logically."
        )

        # --- Step 2: First-Level Improvement via Review ---
        improved_solution = await self.review(pre_solution=initial_solution)

        # --- Step 3: Reflect on the Improved Solution ---
        reflection = await self.reflect(pre_solution=improved_solution)

        # --- Step 4: Conditional Regeneration Only if Needed ---
        if "assumption" in reflection.lower() or "unclear" in reflection.lower() or "error" in reflection.lower():
            # Only if reflection indicates a weakness, use iterative refinement
            final_solution = await self.flexible_custom(
                custom_instruction="Refine the solution based on the following reflection to eliminate assumptions or clarify logic.",
                previous_results=[improved_solution, reflection],
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_reasoning", "recompute"],
                max_iterations=2
            )
            return final_solution
        else:
            # No issues found — return the reviewed solution
            return improved_solution