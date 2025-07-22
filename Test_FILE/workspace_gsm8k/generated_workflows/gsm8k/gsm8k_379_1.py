# Workflow ID: gsm8k_379_1
# Benchmark: gsm8k
# Data Indices: [85, 836]

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
        Diverse and effective workflow using Parallel Ensemble + Iterative Refinement.
        1. Generate 3 distinct solutions via parallel ensemble (each with a different reasoning strategy).
        2. Use ScEnsemble to select the most consistent solution.
        3. Apply iterative refinement: review the selected solution multiple times to improve it progressively.
        4. Final review for polish — ensures clarity and logical soundness before return.
        
        This structure provides robustness through diversity (parallel solutions) and depth through iterative improvement — a fundamentally different logic from the original.
        """

        # Step 1: Parallel Ensemble — Generate 3 independent solutions with varied strategies
        solutions = []
        strategies = [
            "Solve by setting up a proportion based on the given rate.",
            "Break the problem into unit-based calculations (e.g., time per trip).",
            "Use dimensional analysis to convert units step-by-step."
        ]
        for i, strategy in enumerate(strategies):
            sol = await self.custom(
                instruction=f"Apply this reasoning approach: {strategy}. Solve step-by-step with clear explanations."
            )
            solutions.append(sol)

        # Step 2: Select best solution via ScEnsemble — leverages consistency across diverse approaches
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Iterative Refinement — Review the solution multiple times to improve accuracy
        current_solution = best_solution
        for _ in range(2):  # Two iterations of refinement
            revised = await self.review(pre_solution=current_solution)
            current_solution = revised

        # Step 4: Final polish — ensure clarity and completeness
        final_solution = await self.review(pre_solution=current_solution)

        return final_solution