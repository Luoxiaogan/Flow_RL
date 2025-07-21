# Workflow ID: gsm8k_49_1
# Benchmark: gsm8k
# Data Indices: [360, 653]

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
        This is a diverse and robust workflow that combines:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple solution paths
        2. Reflect-and-Regenerate to refine the best candidate using meta-cognition
        3. Iterative Refinement for final polish
        
        The structure ensures diversity in reasoning while maintaining high accuracy through critical reflection and iterative improvement.
        """
        # Step 1: Generate 3 independent solutions via parallel ensemble
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem using a different approach than previous attempts. "
                            "Focus on clear logic and step-by-step breakdown."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best initial solution
        best_initial = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the selected solution — identify hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use reflection to guide a new solution — this time with structured reasoning
        guided_solution = await self.flexible_custom(
            custom_instruction="Based on the reflection, solve the problem with enhanced clarity and precision.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            use_structured_output=True
        )

        # Step 5: Review the guided solution for clarity and correctness
        final_reviewed = await self.review(pre_solution=guided_solution)

        # Step 6: Final iterative refinement — if the reflection suggested a specific issue, address it directly
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            final_answer = await self.flexible_custom(
                custom_instruction="Refine the solution based on the identified assumption or error in the reflection.",
                reasoning_pattern="iterative",
                steps=["identify_issue", "correct", "revalidate"],
                max_iterations=2
            )
        else:
            final_answer = final_reviewed

        return final_answer