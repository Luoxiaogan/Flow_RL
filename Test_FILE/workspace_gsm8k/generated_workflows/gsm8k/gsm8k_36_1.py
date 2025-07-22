# Workflow ID: gsm8k_36_1
# Benchmark: gsm8k
# Data Indices: [884, 608, 265]

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
        Diverse and complex workflow using the Reflect and Regenerate pattern with iterative refinement.
        This is fundamentally different from the existing workflow because:
        - It uses a single initial solution followed by reflection and regeneration (no parallel ensemble).
        - It leverages the FlexibleCustom in an iterative reasoning pattern to guide multiple rounds of improvement.
        - It incorporates a structured feedback loop: generate → reflect → regenerate → review (optional) → final output.
        """
        # Step 1: Generate an initial solution using flexible custom with iterative pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with a clear step-by-step breakdown of the problem.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or oversights
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a new, more informed solution via Custom
        improved_solution = await self.custom(
            instruction=f"Based on this reflection: '{reflection}', rewrite the solution to address potential flaws or missing logic. Be explicit about how each assumption was handled."
        )

        # Step 4: Optional but powerful: Review the improved solution for clarity and correctness
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer