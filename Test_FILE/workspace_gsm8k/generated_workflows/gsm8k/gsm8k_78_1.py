# Workflow ID: gsm8k_78_1
# Benchmark: gsm8k
# Data Indices: [281, 154]

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
        Generate an initial solution, then use reflection to guide two rounds of refinement.
        This pattern leverages meta-cognition — the system critiques its own reasoning before improving it.
        It's fundamentally different from the existing workflow because:
          - Uses `Reflect` to generate critique *before* each refinement (not just after)
          - Applies iterative improvement but guided by internal reflection, not blind review
          - Avoids redundant reviews by using reflection as a filter for what needs fixing
        """

        # Step 1: Initial solution via flexible custom with sequential steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem systematically: identify knowns, unknowns, and required operations.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "formulate_plan", "execute_calculation"]
        )

        # Step 2: Reflect on the initial solution — get insight into potential flaws or gaps
        reflection_1 = await self.reflect(pre_solution=initial_solution)

        # Step 3: First refinement guided by reflection — improve based on self-critique
        first_refined = await self.custom(
            instruction=f"Based on the following reflection: {reflection_1}. Now, revise your solution to address these points."
        )

        # Step 4: Reflect again on the refined solution — now focusing on clarity, logic flow, and completeness
        reflection_2 = await self.reflect(pre_solution=first_refined)

        # Step 5: Final refinement using both original reflection and new one — apply deeper insight
        final_solution = await self.custom(
            instruction=f"Revise the following solution using this reflection: {reflection_2}. Ensure all steps are logically sound and clearly explained."
        )

        return final_solution