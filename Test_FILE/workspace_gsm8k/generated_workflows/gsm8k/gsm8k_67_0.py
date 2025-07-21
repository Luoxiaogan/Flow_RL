# Workflow ID: gsm8k_67_0
# Benchmark: gsm8k
# Data Indices: [14, 185, 235]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Critically reflect on it to uncover potential flaws or improvements.
        4. Use that reflection to guide a new, targeted solution generation.
        This structure ensures robustness (from ensemble) and meta-cognitive refinement (from reflection).
        """
        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on logical decomposition and verification."
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to pick the most accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the best solution to identify weaknesses or missed aspects
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise, thorough, and address any gaps identified."
        )

        return final_answer