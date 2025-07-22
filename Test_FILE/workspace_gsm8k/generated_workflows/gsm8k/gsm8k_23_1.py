# Workflow ID: gsm8k_23_1
# Benchmark: gsm8k
# Data Indices: [712, 431]

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
        Reflect and Regenerate workflow: Generate an initial solution, critically reflect on it to uncover hidden assumptions or errors, then use that reflection to guide a targeted re-solution.
        This is fundamentally different from the existing workflow because:
        - It uses a meta-cognitive loop (Reflect + Custom) instead of parallel ensembling or iterative refinement.
        - The control flow is sequential but deeply reflective — each step builds on the previous one with explicit reasoning about quality.
        - No ensemble selection; instead, the system "learns" from its own mistakes via reflection before finalizing.
        """

        # Step 1: Generate an initial solution using a general-purpose flexible custom approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using clear, logical reasoning.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, missing steps, or flawed logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        # This is the key difference: instead of reviewing or ensembling, we now regenerate based on insight
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution:\n\n{reflection}\n\nUse this feedback to produce a more accurate and robust answer."
        )

        return final_answer