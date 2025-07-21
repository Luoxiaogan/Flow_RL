# Workflow ID: gsm8k_110_1
# Benchmark: gsm8k
# Data Indices: [364, 307, 739]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on its potential flaws, and uses that insight to guide a refined solution.
        A final review ensures clarity and correctness — this mimics human metacognition for improved accuracy.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into explicit steps: identify known quantities, perform operations sequentially, and verify each step."
        )

        # Step 2: Critically reflect on the initial solution — find hidden assumptions, edge cases, or logic gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted solution — this is where meta-cognition improves accuracy
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial approach: '{reflection}'. Now, solve the problem again with improved rigor and attention to detail."
        )

        # Step 4: Final review to polish language, structure, and catch any remaining issues
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution