# Workflow ID: gsm8k_163_0
# Benchmark: gsm8k
# Data Indices: [770, 920]

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
        Robust parallel ensemble workflow using diverse reasoning patterns.
        Generates 3 solutions via different FlexibleCustom configurations,
        then selects the best one with ScEnsemble, followed by a final review.
        """
        # Step 1: Generate 3 distinct solutions using different reasoning strategies
        solutions = []
        
        # Solution 1: Sequential decomposition (analyze → plan → solve → verify)
        sol1 = await self.flexible_custom(
            custom_instruction="Break down the problem logically and solve step-by-step",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        
        # Solution 2: Iterative refinement (start with rough estimate, refine multiple times)
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial guess, then improve iteratively",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration (consider multiple interpretations or methods)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore multiple possible approaches simultaneously",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare", "choose_best"]
        )
        
        solutions.extend([sol1, sol2, sol3])

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review for polishing and catching any remaining errors
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer