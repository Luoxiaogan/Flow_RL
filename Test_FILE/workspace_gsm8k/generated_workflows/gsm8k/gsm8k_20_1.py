# Workflow ID: gsm8k_20_1
# Benchmark: gsm8k
# Data Indices: [494, 791]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        1. Generate 3 independent solutions via parallel approach (fan-out).
        2. Use ScEnsemble to select the best solution.
        3. Critically reflect on that winner to uncover hidden assumptions or gaps.
        4. Use reflection to guide a new, targeted Custom call for final refinement.
        
        This combines parallel robustness with meta-cognitive improvement — fundamentally different from iterative refinement.
        """
        # Step 1: Generate multiple candidate solutions in parallel using FlexibleCustom
        # We use "parallel" reasoning pattern to explore diverse strategies simultaneously
        solutions = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Apply a unique reasoning strategy: e.g., algebraic, visual, or step-by-step arithmetic.",
                reasoning_pattern="parallel",
                steps=["analyze", "model", "compute", "verify"]
            )
            solutions.append(solution)

        # Step 2: Select the most accurate solution using ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify flaws, assumptions, or alternative paths
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a final solution based on reflection — now guided by self-aware critique
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        f"Use this insight to generate a more precise, logically sound, and complete answer."
        )

        return final_answer