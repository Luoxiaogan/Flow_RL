# Workflow ID: gsm8k_132_1
# Benchmark: gsm8k
# Data Indices: [73, 61]

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
        This is a diverse and robust workflow using two distinct patterns:
        1. Iterative Refinement (via FlexibleCustom with iterative pattern) to improve an initial solution.
        2. Reflect-and-Regenerate (using Reflect + Custom) to incorporate meta-cognitive critique into a final revision.

        The flow: 
        - Start with an iterative solution (pattern: refine until stable).
        - Use reflection on the best iteration to identify weaknesses.
        - Regenerate a new solution informed by that reflection.
        - Final review ensures clarity and correctness.
        """

        # --- STEP 1: Generate an initial solution via iterative refinement ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate or assumption, then refine step-by-step for accuracy.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=3
        )

        # --- STEP 2: Critically reflect on the iterative solution ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- STEP 3: Regenerate a new solution based on reflection ---
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection}'. Now solve the problem again, addressing these points explicitly."
        )

        # --- STEP 4: Final polish via Review ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer