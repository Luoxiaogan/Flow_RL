# Workflow ID: gsm8k_178_0
# Benchmark: gsm8k
# Data Indices: [362, 436, 243]

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
        It generates 3 independent solutions with different reasoning styles via FlexibleCustom,
        then selects the best one using ScEnsemble. Finally, reviews the selected solution for clarity.
        """
        # Generate three diverse solutions using different reasoning patterns
        solutions = []
        
        # Solution 1: Sequential reasoning (step-by-step breakdown)
        sol1 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        
        # Solution 2: Iterative refinement (start simple, improve progressively)
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine it in multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "finalize"],
            max_iterations=2
        )
        
        # Solution 3: Branching logic (consider multiple paths and choose the best)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore multiple possible interpretations or methods to solve this.",
            reasoning_pattern="branching",
            steps=["identify_approaches", "evaluate", "select_best"]
        )

        solutions.extend([sol1, sol2, sol3])

        # Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to polish clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer