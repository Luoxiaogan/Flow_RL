# Workflow ID: gsm8k_64_0
# Benchmark: gsm8k
# Data Indices: [562, 449, 848]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (Fan-out/Fan-in) for robust initial solutions
        2. Reflect and Regenerate pattern to refine the best solution
        3. Iterative refinement via FlexibleCustom with iterative reasoning pattern
        """

        # Step 1: Generate multiple independent solutions using parallel ensemble
        solutions = []
        for _ in range(3):  # Generate 3 different approaches
            sol = await self.custom(instruction="Solve the problem by breaking it into clear steps. Consider alternative interpretations of the question.")
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most promising solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify assumptions, gaps, or possible flaws
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, generate a new improved solution using FlexibleCustom with an iterative pattern
        # This step uses structured reasoning steps: analyze → plan → solve → verify
        improved_solution = await self.flexible_custom(
            custom_instruction="Apply systematic reasoning based on the following reflection: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        # Step 5: Final review to polish the answer before returning
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer