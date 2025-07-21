# Workflow ID: gsm8k_106_1
# Benchmark: gsm8k
# Data Indices: [129, 768, 259]

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
        This is a diverse and hybrid workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple candidate solutions
        2. Reflect + Regenerate (fan-in) to critique the best solution and improve it
        3. Iterative refinement for final polish
        
        The structure ensures robustness via diversity (multiple approaches), 
        meta-cognition (reflection), and iterative improvement — all without problem-specific logic.
        """
        # Step 1: Generate 3 independent solutions using parallel ensemble pattern
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by applying a different reasoning strategy each time. First, try step-by-step decomposition. Second, use estimation. Third, work backwards from the expected answer."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to select the strongest candidate
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the selected solution — identify potential flaws or assumptions
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Based on reflection, regenerate a new solution that addresses the identified issues
        improved_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection on its weaknesses: {reflection}. Now, provide a revised solution that explicitly addresses these concerns while maintaining logical rigor."
        )

        # Step 5: Final refinement using iterative Review to ensure clarity and completeness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution