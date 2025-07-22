# Workflow ID: gsm8k_33_1
# Benchmark: gsm8k
# Data Indices: [749, 960, 552]

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
        This workflow uses a novel structure where each refinement is informed by a reflective critique of the previous solution.
        It combines iterative improvement (like the existing workflow) with meta-cognition via the new `Reflect` operator.
        Unlike the existing workflow that just reviews blindly, this one ensures that each iteration is guided by explicit reflection on potential flaws or missed opportunities.
        """

        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into logical parts."
        )

        # Step 2: Reflect on the initial solution to identify possible weaknesses or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution — not just a generic review
        first_refined = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. Now, provide a revised and improved solution based on this insight."
        )

        # Step 4: Reflect again on the first refined solution to uncover deeper issues
        second_reflection = await self.reflect(pre_solution=first_refined)

        # Step 5: Final refinement guided by second reflection — ensuring continuous improvement
        final_solution = await self.custom(
            instruction=f"Based on the reflection: {second_reflection}, refine the solution further to ensure completeness, accuracy, and clarity."
        )

        return final_solution