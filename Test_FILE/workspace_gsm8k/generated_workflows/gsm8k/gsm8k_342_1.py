# Workflow ID: gsm8k_342_1
# Benchmark: gsm8k
# Data Indices: [888, 239, 872]

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
        This is a diverse and robust workflow using:
        1. Iterative Refinement (via FlexibleCustom with iterative pattern)
        2. Reflect-and-Regenerate (using Reflect to critique the result, then guide a new solution)
        
        The logic is fundamentally different from the existing workflow:
        - It uses an iterative loop internally (FlexibleCustom with max_iterations=3)
        - Then applies meta-cognition via Reflect before finalizing
        - No parallel ensemble; instead, one evolving solution refined over time
        - Uses structured reasoning steps in FlexibleCustom for consistency
        """

        # Step 1: Use iterative FlexibleCustom to generate a progressively improved solution
        # This mimics how humans refine their thinking — try once, reflect, try again
        iterative_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3,
            custom_instruction="Start with a rough estimate, then improve through each iteration."
        )

        # Step 2: Critically reflect on the final iterative solution
        reflection = await self.reflect(pre_solution=iterative_solution)

        # Step 3: Based on reflection, generate a final polished answer
        # This ensures we don't just accept the last iteration — we use insight from reflection
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution:\n\n{reflection}\n\nNow, provide a clear, accurate, and well-explained final answer."
        )

        return final_answer