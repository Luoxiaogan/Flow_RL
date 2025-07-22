# Workflow ID: gsm8k_39_1
# Benchmark: gsm8k
# Data Indices: [887, 285, 578]

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
        Iterative Refinement Workflow with FlexibleCustom for structured improvement.
        
        This workflow uses the 'Iterative Refinement' pattern as the core logic:
        1. Generate an initial solution using a flexible sequential approach (step-by-step).
        2. Apply Review twice to progressively refine it — each time improving clarity, correctness, or completeness.
        3. The second review acts as a final polish, ensuring robustness through repeated refinement.
        
        Key differences from existing:
        - No parallel ensemble; instead, focuses on deep iterative improvement.
        - Uses FlexibleCustom with "sequential" reasoning pattern for consistent structure.
        - Only one solution is generated and improved iteratively — no fan-out/fan-in.
        - No reflection-based regeneration; instead, relies on direct, progressive revision via Review.
        - Simpler control flow but more focused on depth of reasoning per step.
        """

        # Step 1: Generate an initial solution using structured, step-by-step reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying key elements of the problem and solving it systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: First refinement — improve clarity, check logic flow
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — ensure accuracy, address potential oversights
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution