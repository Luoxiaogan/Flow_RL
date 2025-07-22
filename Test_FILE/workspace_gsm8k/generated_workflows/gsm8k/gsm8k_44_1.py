# Workflow ID: gsm8k_44_1
# Benchmark: gsm8k
# Data Indices: [797, 674]

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
        Novel workflow combining Reflect-and-Regenerate with Iterative Refinement.
        First, generate an initial solution using a flexible sequential approach.
        Then, reflect on it to identify potential flaws or missing assumptions.
        Based on that reflection, regenerate the solution with targeted improvements.
        Finally, refine iteratively (up to 2 times) to polish the answer — mimicking human metacognition and iterative learning.
        """
        # Step 1: Initial solution via structured sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using logical analysis.",
            reasoning_pattern="sequential",
            steps=["understand", "decompose", "calculate", "validate"]
        )

        # Step 2: Reflect critically on the initial solution — no rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Regenerate solution using the reflection as guidance
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial attempt: '{reflection}'. "
                        f"Provide a revised, more accurate solution now."
        )

        # Step 4: Apply iterative refinement — review and improve up to two times
        current = improved_solution
        for _ in range(2):  # Max 2 iterations of refinement
            refined = await self.review(pre_solution=current)
            if refined == current:  # No change means we've stabilized
                break
            current = refined

        return current