# Workflow ID: gsm8k_73_1
# Benchmark: gsm8k
# Data Indices: [2, 699, 254]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        - First, generate 3 independent solutions using parallel reasoning (fan-out).
        - Select the best one via ScEnsemble.
        - Critically reflect on that winner to identify potential blind spots or assumptions.
        - Use the reflection to guide a targeted re-solution (regeneration), avoiding generic fixes.
        This approach combines robustness (multiple starting points) with meta-cognition (reflection-driven improvement).
        """
        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):
            candidate = await self.flexible_custom(
                custom_instruction="Apply a unique reasoning strategy to solve this problem.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_candidates.append(candidate)

        # Step 2: Choose the best candidate using ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the chosen solution — critique it without rewriting
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution based on the reflection
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Use this insight to construct a more accurate and thorough solution."
        )

        return final_solution