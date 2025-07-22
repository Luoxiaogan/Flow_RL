# Workflow ID: gsm8k_23_0
# Benchmark: gsm8k
# Data Indices: [712, 431]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 distinct solutions via FlexibleCustom with different patterns,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # Step 1: Generate multiple solutions using different reasoning patterns
        solutions = []
        
        # Solution 1: Sequential decomposition (step-by-step breakdown)
        solution1 = await self.flexible_custom(
            custom_instruction="Break the problem into clear steps: identify knowns, unknowns, and apply operations in order.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "compute", "verify"]
        )
        
        # Solution 2: Iterative refinement (start rough, improve)
        solution2 = await self.flexible_custom(
            custom_instruction="Begin with an estimate or initial approach, then refine iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration (multiple interpretations)
        solution3 = await self.flexible_custom(
            custom_instruction="Consider alternative ways to interpret and solve the problem.",
            reasoning_pattern="parallel",
            steps=["analyze_alternatives", "compare_approaches", "select_best"]
        )
        
        solutions.extend([solution1, solution2, solution3])

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to catch any remaining issues or ambiguities
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer