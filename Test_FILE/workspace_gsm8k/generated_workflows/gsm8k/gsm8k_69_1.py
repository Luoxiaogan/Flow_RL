# Workflow ID: gsm8k_69_1
# Benchmark: gsm8k
# Data Indices: [658, 90, 464]

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
        This is a novel workflow using the Reflect-and-Regenerate pattern with iterative refinement via FlexibleCustom.
        1. Use FlexibleCustom in 'iterative' mode to generate an initial solution with structured steps.
        2. Critically reflect on that solution — identifying assumptions, edge cases, or logical gaps.
        3. Regenerate using a custom instruction informed by reflection.
        4. Finally, refine the regenerated solution using Review for polish and clarity.
        
        This approach prioritizes deep metacognition: first solve, then question your own reasoning, then improve.
        """

        # Step 1: Generate an initial solution using iterative flexible custom — this ensures step-by-step decomposition
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect critically — do not rewrite yet! Identify potential flaws, oversights, or missing logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Regenerate based on reflection — now we use the insight from reflection to guide a new, improved attempt
        improved_instruction = (
            f"Here is the original solution:\n{initial_solution}\n\n"
            f"And here is the reflection on its limitations:\n{reflection}\n\n"
            "Using this feedback, provide a revised solution that addresses these points while maintaining clear, structured reasoning."
        )
        final_solution = await self.custom(instruction=improved_instruction)

        # Step 4: Final polish — review for clarity, completeness, and correctness
        polished_answer = await self.review(pre_solution=final_solution)

        return polished_answer