# Workflow ID: gsm8k_236_1
# Benchmark: gsm8k
# Data Indices: [95, 178]

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
        This is a diverse and complex workflow using:
        1. Iterative Refinement via FlexibleCustom (with 'iterative' pattern) to progressively improve the solution
        2. Reflect and Regenerate as the core reasoning loop — not just once, but in a structured iterative cycle
        3. No parallel ensemble; instead, we focus on deep internal refinement guided by reflection
        4. Uses structured output from FlexibleCustom to ensure clarity at each iteration
        """

        # Step 1: Use FlexibleCustom with iterative reasoning pattern to generate an initial solution
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving the problem using an iterative approach.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "execute", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or logical flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use that reflection to guide a new FlexibleCustom call with enhanced steps
        improved_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: '{reflection}', refine your approach to address potential issues. Focus on clarity, completeness, and correctness.",
            reasoning_pattern="sequential",
            steps=["analyze_assumptions", "correct_flaws", "recompute", "validate"],
            use_structured_output=True
        )

        # Step 4: Final review to polish the answer — ensures readability and correctness before return
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer