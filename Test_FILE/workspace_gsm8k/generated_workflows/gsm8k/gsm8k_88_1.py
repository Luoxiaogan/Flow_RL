# Workflow ID: gsm8k_88_1
# Benchmark: gsm8k
# Data Indices: [862, 180]

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
        Iterative Refinement with Reflective Guidance: 
        This workflow uses a meta-cognitive loop where each refinement is guided by a reflection on the previous solution.
        It differs from the existing workflow by incorporating reflective critique before generating the next version,
        rather than applying blind reviews. This ensures that improvements are intentional and targeted.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution — identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via Custom
        first_improved = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Now, provide a more accurate and complete solution based on this feedback."
        )

        # Step 4: Reflect again on the improved solution to catch any remaining issues
        second_reflection = await self.reflect(pre_solution=first_improved)

        # Step 5: Final refinement using Review — now with explicit guidance from reflection
        final_solution = await self.review(
            pre_solution=first_improved,
            instruction=f"Based on the reflection: {second_reflection}, improve clarity, accuracy, and completeness."
        )

        return final_solution