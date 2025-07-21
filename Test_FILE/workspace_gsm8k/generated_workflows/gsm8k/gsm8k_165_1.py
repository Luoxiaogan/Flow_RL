# Workflow ID: gsm8k_165_1
# Benchmark: gsm8k
# Data Indices: [205, 941]

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
        This workflow uses a novel 'Iterative Refinement with Reflection' pattern.
        It starts with a flexible custom solution using an iterative reasoning pattern,
        then applies reflection to critique the result, and finally refines it further
        through targeted review. This combines structured iteration with meta-cognitive feedback.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate a step-by-step solution
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem systematically.",
            reasoning_pattern="iterative",
            steps=["understand", "analyze", "compute", "verify"],
            max_iterations=2
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a more focused refinement via Custom
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}, revise your approach. Focus on addressing any assumptions or gaps identified. Provide a clear, final answer."
        )

        # Step 4: Apply one final Review step to polish the solution before returning
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution