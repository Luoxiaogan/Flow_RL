# Workflow ID: gsm8k_160_1
# Benchmark: gsm8k
# Data Indices: [544, 924]

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
        Iterative Refinement with Reflect-Driven Improvement (Fundamentally Different Logic).
        Uses the new 'Reflect' operator to guide iterative refinement — not just mechanical review.
        This creates a meta-cognitive loop: generate → reflect → improve → repeat.
        """
        # Step 1: Generate an initial solution using flexible custom with a structured sequential pattern
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem systematically and show all steps clearly."
        )

        # Step 2: Reflect on the initial solution — identify assumptions, gaps, or ambiguities
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined custom generation (not just a generic review)
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Reconstruct the answer with clearer logic, addressing any weaknesses identified."
        )

        # Step 4: Apply Review to polish clarity and correctness (second pass of improvement)
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution