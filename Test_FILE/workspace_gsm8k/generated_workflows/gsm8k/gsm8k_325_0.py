# Workflow ID: gsm8k_325_0
# Benchmark: gsm8k
# Data Indices: [14, 860, 335]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        Generates 3 distinct solutions via different reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # --- Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns ---
        solutions = []
        
        # Solution 1: Sequential approach — break down logically step-by-step
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this math word problem by identifying knowns, unknowns, and applying operations in sequence.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "form_equations", "solve"]
        )
        
        # Solution 2: Iterative refinement — start with an estimate, improve it
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with a reasonable guess, then refine your answer through logical checks.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "validate", "adjust"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration — consider multiple interpretations
        sol3 = await self.flexible_custom(
            custom_instruction="Explore different possible interpretations of the problem statement to ensure no assumptions are missed.",
            reasoning_pattern="parallel",
            steps=["interpret_alternatives", "evaluate_consistency", "select_best"]
        )
        
        solutions.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to pick the most consistent solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for clarity, completeness, and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer