# Workflow ID: gsm8k_71_0
# Benchmark: gsm8k
# Data Indices: [470, 924, 666]

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
        Step 1: Generate multiple candidate solutions in parallel (fan-out).
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Critically reflect on the selected solution to uncover blind spots.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- Step 1: Parallel Ensemble (Fan-out) ---
        # Generate 3 independent initial solutions using Custom
        solutions = []
        for i in range(3):
            instruction = "Solve the problem step-by-step, focusing on clear reasoning. Consider different possible interpretations of ambiguous parts."
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # --- Step 2: Fan-in with ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Reflect on the Best Solution ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Based on Reflection ---
        # Use FlexibleCustom with an iterative pattern to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction="Use the following reflection to improve your answer: " + reflection_text,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_reasoning", "recompute"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution