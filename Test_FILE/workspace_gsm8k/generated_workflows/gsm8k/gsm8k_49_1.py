# Workflow ID: gsm8k_49_1
# Benchmark: gsm8k
# Data Indices: [134, 806, 328]

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
        1. Iterative Refinement (with FlexibleCustom in iterative mode) - Start with an initial approach, then refine iteratively
        2. Branching Logic Based on Reflection - Use the reflection to decide whether to continue refining or switch strategies
        3. Parallel Ensemble for Final Validation - After refinement, generate multiple final candidates to ensure robustness

        Key differences from existing:
        - Uses iterative pattern first (not parallel), then branches based on reflection
        - Doesn't rely solely on ScEnsemble at the end; instead uses it as a validation step after branching logic
        - Introduces conditional control flow: if reflection suggests fundamental flaw, regenerate; else, polish
        """

        # Step 1: Initial solution via iterative FlexibleCustom (3 iterations max)
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving this math problem using estimation and logical deduction.",
            reasoning_pattern="iterative",
            steps=["estimate", "calculate", "verify"],
            max_iterations=3
        )

        # Step 2: Reflect on the initial solution to detect flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Conditional branching based on reflection content
        # If reflection indicates a major conceptual issue, regenerate with new strategy
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "flaw" in reflection.lower():
            regenerated_solution = await self.custom(
                instruction=f"Based on the reflection: '{reflection}'. "
                            f"Reconstruct the solution using a completely different approach—focus on identifying constraints and working backwards."
            )
            final_answer = await self.review(pre_solution=regenerated_solution)
        else:
            # Otherwise, apply one more round of refinement
            final_answer = await self.review(pre_solution=initial_solution)

        # Step 4: Final validation using parallel ensemble — generate 3 variants of the final answer
        # This ensures robustness even if the previous step had subtle issues
        final_candidates = []
        for _ in range(3):
            candidate = await self.flexible_custom(
                custom_instruction="Rephrase the final solution clearly and concisely, ensuring all steps are logically sound.",
                reasoning_pattern="sequential",
                steps=["restate", "validate", "explain"]
            )
            final_candidates.append(candidate)

        # Final output: pick best among the three rephrased versions
        return await self.sc_ensemble(solutions=final_candidates)