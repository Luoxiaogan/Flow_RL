# Workflow ID: gsm8k_380_1
# Benchmark: gsm8k
# Data Indices: [927, 468]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Parallel Ensemble.
        1. Generate 3 independent solutions (parallel).
        2. Use ScEnsemble to select the best one.
        3. Critically reflect on that solution to uncover hidden assumptions or errors.
        4. Regenerate a final answer based on the reflection — this ensures meta-cognitive improvement.
        This logic differs from the existing workflow by introducing a reflective loop after ensemble selection,
        rather than just reviewing the ensemble result directly.
        """
        # --- STEP 1: Generate 3 different solutions in parallel via FlexibleCustom with varied strategies ---
        solutions = []

        # Strategy 1: Sequential reasoning — structured step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Break the problem into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        solutions.append(sol1)

        # Strategy 2: Iterative refinement — start rough, improve iteratively
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial approach, then refine it through multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_attempt", "evaluate", "improve"],
            max_iterations=2
        )
        solutions.append(sol2)

        # Strategy 3: Creative assumption-based solving — test consistency with assumed values
        sol3 = await self.custom(
            instruction="Assume a total quantity, solve for that assumption, and verify if it leads to consistent results."
        )
        solutions.append(sol3)

        # --- STEP 2: Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect critically on the selected solution to identify potential flaws or missed insights ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate the final answer using the reflection as a guide ---
        # This is the key difference: instead of just polishing, we now *re-reason* based on the critique
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Use this insight to produce a more accurate and logically sound answer."
        )

        return final_answer