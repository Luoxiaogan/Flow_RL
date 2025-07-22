# Workflow ID: gsm8k_51_1
# Benchmark: gsm8k
# Data Indices: [683, 971, 316]

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
        Diverse workflow using the 'Parallel Ensemble + Reflect and Regenerate' pattern.
        This approach first generates multiple independent solutions (parallel), 
        then selects the best one via ensemble, and finally applies a reflective critique 
        to refine it into a superior, well-justified answer — combining robustness with meta-cognition.
        """
        # Step 1: Generate 3 diverse initial solutions in parallel using FlexibleCustom with different reasoning patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Solve using a step-by-step decomposition strategy.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )
        
        solution2 = await self.flexible_custom(
            custom_instruction="Solve by exploring multiple possible interpretations first.",
            reasoning_pattern="branching",
            steps=["identify_interpretations", "evaluate_options", "choose_best", "solve"]
        )
        
        solution3 = await self.flexible_custom(
            custom_instruction="Use iterative refinement starting from an estimate.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "finalize"],
            max_iterations=2
        )

        # Step 2: Use ScEnsemble to select the most accurate of the three
        candidate_solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Critically reflect on the selected best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Generate a final improved solution based on the reflection
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the best solution: {reflection}. "
                        f"Re-solve the problem with enhanced clarity, addressing any overlooked assumptions or logical gaps."
        )

        return final_solution