# Workflow ID: gsm8k_341_1
# Benchmark: gsm8k
# Data Indices: [513, 621, 132]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using Review.
        This approach prioritizes progressive improvement over ensemble diversity or parallel exploration.
        It mirrors how humans solve complex problems — starting with a rough answer and refining it step-by-step.
        """
        # Step 1: Generate an initial solution using flexible custom with a basic sequential plan
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Apply iterative refinement — review once to improve clarity and correctness
        first_refinement = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second refinement — further polish based on first revision
        second_refinement = await self.review(pre_solution=first_refinement)

        # Step 4: Final reflection to catch any remaining issues before returning
        final_reflection = await self.reflect(pre_solution=second_refinement)

        # Step 5: Use the reflection to guide a final polishing pass (not just review, but informed revision)
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{final_reflection}'. "
                        f"Provide the final, fully refined solution to the problem."
        )

        return final_answer