# Workflow ID: gsm8k_109_1
# Benchmark: gsm8k
# Data Indices: [526, 87]

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
        Uses a reflective loop to guide improvement — generate solution, reflect on it, then use reflection to inform the next refinement.
        This is fundamentally different from the existing workflow because it introduces meta-cognition (reflection) as a driver for iterative improvement,
        rather than just applying mechanical reviews. It also uses FlexibleCustom to structure the iterative process logically.
        """

        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=1,
            custom_instruction="Break the problem into knowns, unknowns, and required operations."
        )

        # Step 2: Reflect critically on the initial solution — identify potential flaws or missing elements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a second iteration via FlexibleCustom
        refined_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_plan", "recompute", "validate"],
            max_iterations=2,
            custom_instruction=f"Based on this reflection: {reflection}. Now refine your solution by addressing these points."
        )

        # Step 4: Final review to polish clarity and correctness
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution