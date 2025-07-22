# Workflow ID: gsm8k_262_1
# Benchmark: gsm8k
# Data Indices: [376, 907]

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
        1. Generate 3 independent solutions using parallel reasoning (Fan-out).
        2. Use ScEnsemble to select the best one.
        3. Critically reflect on the selected solution to uncover hidden assumptions or gaps.
        4. Regenerate a final improved solution based on that reflection (Meta-cognitive loop).
        
        This design combines two distinct patterns:
        - Parallel Ensemble for robustness against flawed individual reasoning
        - Reflect-and-Regenerate for meta-level improvement beyond simple review
        """
        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by considering alternative approaches and explaining each step clearly."
            )
            solution_candidates.append(candidate)

        # Step 2: Select the best solution via ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the best solution — critique its logic, assumptions, and completeness
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, more informed solution generation
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, provide a refined and improved solution that addresses the identified issues."
        )

        return final_answer