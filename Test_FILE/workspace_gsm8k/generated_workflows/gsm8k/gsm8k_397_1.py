# Workflow ID: gsm8k_397_1
# Benchmark: gsm8k
# Data Indices: [149, 692, 433]

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
        Diverse and robust workflow using Parallel Ensemble with varied reasoning strategies.
        Step 1: Generate 3 solutions using FlexibleCustom with different reasoning patterns (sequential, iterative, branching).
        Step 2: Use ScEnsemble to select the most consistent solution across all three.
        Step 3: Final Review for clarity, completeness, and error-checking — this ensures high-quality output without overfitting to any single strategy.
        
        This design differs from the existing one by:
        - Using FlexibleCustom with distinct reasoning patterns instead of identical prompts in a loop
        - Avoiding reflection-based regeneration; instead, relying on ensemble diversity + final review
        - Employing structured, pattern-driven generation rather than pure randomness
        """

        # --- PARALLEL ENSEMBLE WITH DIVERSE REASONING STRATEGIES ---
        solutions = []

        # Strategy 1: Sequential decomposition
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps: identify knowns, unknowns, and apply appropriate operations.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"]
        )
        solutions.append(seq_solution)

        # Strategy 2: Iterative refinement
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine through multiple passes until you converge on the correct answer.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Strategy 3: Branching logic (conditional paths based on intermediate results)
        branch_solution = await self.flexible_custom(
            custom_instruction="Consider alternative interpretations or paths. If one path fails, try another. Synthesize the best outcome.",
            reasoning_pattern="branching",
            steps=["analyze_options", "evaluate_paths", "choose_best"]
        )
        solutions.append(branch_solution)

        # --- SCENSEMBLE (Fan-in): Select the most consistent solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- FINAL REVIEW FOR QUALITY CONTROL ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer