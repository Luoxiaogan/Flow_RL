# Workflow ID: gsm8k_252_1
# Benchmark: gsm8k
# Data Indices: [245, 835]

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
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        Generates an initial solution, then applies Review twice to progressively improve it.
        This mimics how humans refine their reasoning—first draft, then feedback, then polish.
        """
        # Step 1: Generate a first-pass solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into small steps. Show each calculation clearly."
        )

        # Step 2: First refinement — critique and rewrite based on internal logic
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply deeper scrutiny for clarity and correctness
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        # Optional but valuable: Reflect on the final solution to catch any lingering issues
        reflection = await self.reflect(pre_solution=refined_solution_2)

        # Final step: Use the reflection to guide a last-minute improvement (if needed)
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Now, provide the final, most accurate answer."
        )

        return final_answer