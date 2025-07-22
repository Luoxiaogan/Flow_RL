# Workflow ID: gsm8k_328_1
# Benchmark: gsm8k
# Data Indices: [889, 787]

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
        This workflow uses a novel 'Reflect and Regenerate' pattern with iterative refinement via FlexibleCustom.
        It begins with an initial solution, then reflects on it to uncover hidden assumptions or gaps.
        Instead of a single fix, it uses FlexibleCustom in 'iterative' mode to systematically improve the solution across multiple passes — mimicking how humans refine reasoning through metacognition.
        
        Key differences from the existing workflow:
        - Uses `FlexibleCustom` with `reasoning_pattern="iterative"` for structured improvement, not just one reflection → custom pass.
        - Does NOT rely on a single final regen; instead, it builds a multi-step refinement loop that learns from its own earlier attempts.
        - Introduces internal feedback within the same operator (via max_iterations), making this logic fundamentally different than the existing step-by-step reflection + fixed re-generation.
        """
        # Step 1: Generate an initial solution using general-purpose reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by identifying knowns, unknowns, setting up equations, and computing the answer. Be explicit about each step."
        )

        # Step 2: Reflect on the initial solution to uncover potential flaws or missed aspects
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use FlexibleCustom in iterative mode to progressively refine the solution based on the reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, refine your approach: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3,
            use_structured_output=True
        )

        return refined_solution