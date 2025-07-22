# Workflow ID: gsm8k_42_1
# Benchmark: gsm8k
# Data Indices: [499, 870]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out): Generate 3 independent solutions via FlexibleCustom with different reasoning patterns.
        2. Reflect and Regenerate: Take the best solution from the ensemble, reflect on it, then regenerate a final improved version.

        This design ensures robustness through parallel exploration and meta-cognitive refinement — fundamentally different from the original's single-path approach.
        """
        # Step 1: Generate multiple solutions in parallel using different reasoning strategies
        solution_a = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["identify", "formulate", "compute", "verify"],
            custom_instruction="Solve step-by-step using clear logical progression."
        )
        
        solution_b = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2,
            custom_instruction="Start with an estimate, then improve iteratively."
        )
        
        solution_c = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["analyze_options", "choose_path", "execute"],
            custom_instruction="Consider multiple possible approaches before deciding."
        )

        # Step 2: Use ScEnsemble to select the best solution from the three
        candidate_solutions = [solution_a, solution_b, solution_c]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Critically reflect on the selected best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, targeted generation of the final answer
        final_solution = await self.custom(
            instruction=f"Based on this reflection: '{reflection}', produce a refined, accurate, and well-structured solution. "
                        f"Ensure all assumptions are validated and no steps are skipped."
        )

        return final_solution