# Workflow ID: gsm8k_58_1
# Benchmark: gsm8k
# Data Indices: [989, 717]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern with FlexibleCustom.
        It uses a structured, multi-step iterative approach to progressively refine the solution,
        ensuring that each iteration builds on the previous one — ideal for problems requiring careful
        step-by-step correction and validation.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate an initial solution
        # with a defined reasoning structure (analyze → plan → solve → verify)
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by analyzing the problem, planning your approach, solving it, and verifying the result.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missed logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a second round of iterative refinement
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}, "
                               f"re-run the iterative process focusing on improving accuracy and clarity.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3
        )

        return refined_solution