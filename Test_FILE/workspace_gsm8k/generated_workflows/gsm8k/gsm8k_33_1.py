# Workflow ID: gsm8k_33_1
# Benchmark: gsm8k
# Data Indices: [680, 844]

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
        This is a diverse and iterative refinement-based workflow using the Reflect-and-Regenerate pattern.
        It starts with an initial solution, then uses Reflect to critique it, and finally regenerates a better solution based on that reflection.
        This mimics meta-cognitive reasoning: think → reflect → improve.
        """
        # Step 1: Generate an initial solution using FlexibleCustom in iterative mode (with max_iterations=1 for first pass)
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using structured reasoning.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=1
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or logical flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new Custom call that improves upon the original
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again with greater attention to detail and accuracy."
        )

        # Step 4: Final review pass to polish clarity and correctness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution