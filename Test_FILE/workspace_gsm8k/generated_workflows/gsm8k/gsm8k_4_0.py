# Workflow ID: gsm8k_4_0
# Benchmark: gsm8k
# Data Indices: [91, 654]

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
        Generates 3 distinct solutions via FlexibleCustom with different reasoning patterns,
        then selects the best one using ScEnsemble. Final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using different reasoning strategies ---
        solutions = []
        
        # Solution 1: Sequential approach — step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Solve the problem logically by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "formulate_equations", "solve"]
        )
        
        # Solution 2: Iterative refinement — start with an estimate, improve iteratively
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate and refine your answer through multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "adjust"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration — consider multiple interpretations
        sol3 = await self.flexible_custom(
            custom_instruction="Explore different possible interpretations of the problem and solve each independently.",
            reasoning_pattern="parallel",
            steps=["interpret_1", "interpret_2", "compare"]
        )

        solutions.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer