# Workflow ID: gsm8k_132_1
# Benchmark: gsm8k
# Data Indices: [721, 858, 746]

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
        This workflow uses the 'Reflect and Regenerate' pattern as its core logic.
        It generates an initial solution, critically reflects on it to identify potential flaws or improvements,
        then uses that reflection to guide a new, higher-quality solution — mimicking human metacognition.
        
        Key differences from existing workflow:
        - Uses Reflect + Custom (not ScEnsemble) for iterative improvement
        - No parallel solutions; instead, one solution is refined based on meta-cognitive feedback
        - Focuses on internal reasoning quality rather than external consensus
        """

        # --- STEP 1: Generate an initial solution using flexible custom with sequential reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by identifying knowns, defining relationships, applying operations, and computing the final answer.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "apply_operations", "compute_final_answer"]
        )

        # --- STEP 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Use the reflection to generate a superior, targeted solution ---
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                       f"Based on this insight, now provide a revised and improved solution."
        )

        # --- STEP 4: Final review to ensure clarity and correctness of the improved solution ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer