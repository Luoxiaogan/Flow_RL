# Workflow ID: gsm8k_377_0
# Benchmark: gsm8k
# Data Indices: [337, 702, 165]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble (robustness).
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on that solution to uncover potential flaws or missed assumptions.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble ---
        solutions = []
        for _ in range(3):  # Generate 3 different approaches
            sol = await self.custom(
                instruction="Solve this math word problem by breaking it into clear steps. Consider multiple interpretations if applicable."
            )
            solutions.append(sol)
        
        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        final_instruction = (
            f"Given the initial solution and the following reflection:\n\n"
            f"{reflection}\n\n"
            "Now, synthesize a new, more accurate and logically sound solution based on the reflection above."
        )

        final_solution = await self.flexible_custom(
            custom_instruction=final_instruction,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "reconstruct_logic", "validate_steps"],
            max_iterations=2
        )

        return final_solution