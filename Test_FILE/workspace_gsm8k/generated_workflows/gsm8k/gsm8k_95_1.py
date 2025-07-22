# Workflow ID: gsm8k_95_1
# Benchmark: gsm8k
# Data Indices: [364, 206, 697]

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
        It starts with an initial solution, then applies two rounds of review to progressively improve clarity, accuracy, and completeness.
        This mimics how humans refine their thinking through repeated scrutiny — a powerful approach for complex math problems.
        """
        # Step 1: Generate an initial solution using a structured, step-by-step prompt
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into clear steps: identify known quantities, apply operations in order, and show all intermediate calculations."
        )

        # Step 2: First refinement — review to catch errors or missing logic
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — another review pass to polish reasoning and ensure correctness
        second_refined = await self.review(pre_solution=first_refined)

        # Optional: Add reflection-based meta-cognition (not used in existing workflow) to deepen improvement
        # This adds a novel layer of self-awareness not present in the original
        reflection = await self.reflect(pre_solution=second_refined)
        
        # Final step: Use the reflection to guide a final custom rewrite if needed
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, provide a final, polished version of the solution that addresses any concerns raised above."
        )

        return final_answer