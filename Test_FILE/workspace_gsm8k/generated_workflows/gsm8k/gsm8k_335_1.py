# Workflow ID: gsm8k_335_1
# Benchmark: gsm8k
# Data Indices: [952, 523]

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
        Diverse and effective workflow using Parallel Ensemble with a twist: 
        1. Generate 3 solutions via flexible custom in parallel (using different reasoning patterns).
        2. Use ScEnsemble to select the best one.
        3. Apply a final review for polish — not refinement, but clarity and completeness.
        
        This differs from the existing workflow by:
        - Using FlexibleCustom with distinct reasoning patterns (sequential, branching, iterative) instead of just generating varied instructions.
        - Skipping reflection-based regeneration — focusing on ensemble selection + final polishing.
        - Emphasizing structural diversity in generation rather than post-hoc critique loops.
        """

        # --- Step 1: Parallel Ensemble via FlexibleCustom with Different Patterns ---
        # Each solution uses a unique reasoning strategy to reduce bias
        solutions = []
        patterns = ["sequential", "branching", "iterative"]
        for i, pattern in enumerate(patterns):
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem by following the steps outlined in the reasoning pattern.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1,
                use_structured_output=True
            )
            solutions.append(solution)

        # --- Step 2: Select Best Solution via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for Clarity and Completeness ---
        # No regeneration — just clean-up and consistency check
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer