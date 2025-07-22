# Workflow ID: gsm8k_264_1
# Benchmark: gsm8k
# Data Indices: [129, 72]

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
        Diverse and complex workflow combining Iterative Refinement + Reflect & Regenerate.
        Step 1: Use FlexibleCustom in iterative mode to generate a progressively refined solution.
        Step 2: After refinement, reflect on the final result to identify potential blind spots.
        Step 3: Use that reflection to guide a new Custom-based solution — not just a fix, but a re-imagined approach.
        This is fundamentally different from the existing workflow because it uses iterative internal refinement first, then meta-cognitive reflection before a final regeneration — not parallel ensemble followed by one reflection.
        """
        # --- ITERATIVE REFINEMENT WITH FLEXIBLECUSTOM ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin with an initial estimate and refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "analyze_assumptions", "adjust_for_errors", "validate"],
            max_iterations=3
        )

        # --- REFLECT ON THE FINAL ITERATIVE SOLUTION ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- USE REFLECTION TO GUIDED REGENERATION (NOT A SIMPLE FIX) ---
        final_answer = await self.custom(
            instruction=f"Given the following iterative solution: {iterative_solution}. "
                        f"And this critical reflection: {reflection}. "
                        "Now, solve the problem again using a completely different strategy or perspective. Do not simply correct the previous answer — rethink the entire approach."
        )

        return final_answer