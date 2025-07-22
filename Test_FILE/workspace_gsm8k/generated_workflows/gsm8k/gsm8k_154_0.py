# Workflow ID: gsm8k_154_0
# Benchmark: gsm8k
# Data Indices: [314, 976, 512]

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
        1. Parallel Ensemble (Fan-out) to generate multiple initial solutions
        2. Reflect + Regenerate pattern to improve the best solution based on critical reflection
        3. Iterative Refinement using FlexibleCustom for final polish
        """

        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_pool = []
        for i in range(3):  # Generate 3 different approaches
            instruction = "Solve the problem step-by-step using a clear reasoning path. Break down the problem into smaller parts and show your work."
            solution = await self.custom(instruction=instruction)
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the chosen solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, generate a new improved solution
        improved_instruction = f"Given the initial solution and the following reflection: {reflection}. Now, provide a revised and more accurate solution that addresses potential flaws or omissions."
        final_solution = await self.custom(instruction=improved_instruction)

        # Step 5: Optional iterative refinement using FlexibleCustom with sequential steps
        # This adds another layer of structured reasoning — e.g., verify, explain, finalize
        refined_solution = await self.flexible_custom(
            custom_instruction="Refine the solution by verifying each step, explaining assumptions, and ensuring clarity.",
            reasoning_pattern="sequential",
            steps=["verify", "explain_assumptions", "finalize"]
        )

        return refined_solution