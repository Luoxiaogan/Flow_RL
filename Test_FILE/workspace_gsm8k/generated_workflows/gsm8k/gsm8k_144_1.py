# Workflow ID: gsm8k_144_1
# Benchmark: gsm8k
# Data Indices: [219, 151, 137]

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
        Diverse and efficient workflow using a Parallel Ensemble followed by Reflect-based refinement.
        This approach combines robustness (multiple solutions) with meta-cognition (reflection-guided improvement).
        It avoids single-point failure and ensures high-quality output through both diversity and critical thinking.
        """

        # Step 1: Generate multiple independent solutions in parallel to explore different reasoning paths
        solution_candidates = []
        for i in range(3):  # Use 3 diverse approaches via FlexibleCustom with different reasoning patterns
            if i == 0:
                # Sequential reasoning: break into steps
                candidate = await self.flexible_custom(
                    custom_instruction="Solve the problem step-by-step with clear explanations.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start rough, then improve
                candidate = await self.flexible_custom(
                    custom_instruction="Begin with an estimate, then refine it iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "final_answer"],
                    max_iterations=2
                )
            else:
                # Branching logic: consider alternative interpretations or assumptions
                candidate = await self.flexible_custom(
                    custom_instruction="Consider multiple possible interpretations of the problem statement.",
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "explore_branches", "select_best"]
                )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to select the best solution from the candidates
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the selected solution — identify potential blind spots or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final, targeted improvement
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        "Now, produce a revised answer that addresses these points while maintaining clarity and correctness."
        )

        return final_solution