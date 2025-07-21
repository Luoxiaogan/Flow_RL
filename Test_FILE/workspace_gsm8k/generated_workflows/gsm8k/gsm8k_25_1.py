# Workflow ID: gsm8k_25_1
# Benchmark: gsm8k
# Data Indices: [483, 685, 764]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions using parallel approach.
        2. Select the best one via ScEnsemble.
        3. Reflect on the selected solution to identify potential blind spots.
        4. Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        This combines robustness (from ensemble) with meta-cognition (from reflection).
        """
        # Step 1: Generate multiple candidate solutions in parallel
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem by considering different possible interpretations or strategies.")
            solutions.append(sol)

        # Step 2: Enforce quality through ensemble selection
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — do not rewrite yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate using the reflection as guidance
        final_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "reformulate_approach", "solve_with_insight", "verify"],
            custom_instruction=f"Based on this reflection: '{reflection}', generate a refined solution that addresses potential weaknesses.",
            max_iterations=2
        )

        return final_solution