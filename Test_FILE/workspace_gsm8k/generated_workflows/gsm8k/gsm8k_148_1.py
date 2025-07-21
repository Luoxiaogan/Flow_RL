# Workflow ID: gsm8k_148_1
# Benchmark: gsm8k
# Data Indices: [260, 159]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It emphasizes meta-cognition by first generating a solution, then critically reflecting on it,
        and finally using that reflection to produce a superior, targeted answer — avoiding redundancy
        while ensuring logical depth and precision. This differs from the existing workflow by focusing
        solely on reflection as a catalyst for regeneration rather than iterative refinement.
        """

        # Step 1: Generate an initial solution using a flexible, structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "break_down", "calculate", "check"],
            custom_instruction="Solve this math problem by clearly identifying knowns, unknowns, formulas, and units. Show your work step-by-step."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or logical flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, focused Custom call — no iteration, just one high-quality regen
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, provide a revised and improved answer. Focus on correcting any identified issues and ensure all steps are logically sound and unit-consistent."
        )

        return final_solution