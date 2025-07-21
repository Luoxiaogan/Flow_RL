# Workflow ID: gsm8k_1_0
# Benchmark: gsm8k
# Data Indices: [313, 203, 892]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using Review.
        This pattern ensures gradual improvement by identifying and correcting errors or omissions step-by-step.
        """
        # Step 1: Generate an initial solution using a structured reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with clear identification of knowns and unknowns, then apply logical steps to reach a conclusion.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_logic", "compute_answer"]
        )

        # Step 2: First refinement — improve clarity, structure, and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — ensure no assumptions were missed and all logic is sound
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined