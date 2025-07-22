# Workflow ID: gsm8k_283_1
# Benchmark: gsm8k
# Data Indices: [943, 810, 448]

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
        
        This workflow combines two distinct patterns:
        1. **Parallel Ensemble**: Generate 3 independent solutions using different reasoning styles.
        2. **Reflect and Regenerate**: Critically reflect on the best solution, then regenerate a refined version based on that reflection.
        
        Why it's different:
        - Uses parallel generation (not sequential) → avoids single-point failure
        - Introduces meta-cognition via `Reflect` → improves quality beyond simple review
        - Avoids iterative refinement in favor of structured feedback-driven regeneration
        - Employs ensemble selection before any refinement → ensures we start with the strongest candidate
        """
        # Step 1: Generate 3 diverse initial solutions using flexible custom with different reasoning patterns
        solutions = []
        for i in range(3):
            pattern = ["sequential", "parallel", "iterative"][i % 3]
            step_list = ["analyze", "plan", "solve", "verify"]
            
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem using a structured approach.",
                previous_results=None,
                reasoning_pattern=pattern,
                steps=step_list
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the chosen solution — identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution informed by the reflection
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity, accuracy, and completeness."
        )

        return final_answer