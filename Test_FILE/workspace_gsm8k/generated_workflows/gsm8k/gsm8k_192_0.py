# Workflow ID: gsm8k_192_0
# Benchmark: gsm8k
# Data Indices: [627, 199]

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
        Robust parallel ensemble workflow for general math problem solving.
        Generates 3 diverse solutions using different reasoning patterns,
        then selects the best one via ScEnsemble, followed by a final review.
        """
        # --- PARALLEL ENSEMBLE: Generate 3 distinct solutions ---
        solution_list = []
        
        # Solution 1: Sequential step-by-step decomposition
        sol1 = await self.flexible_custom(
            custom_instruction="Break the problem into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "identify", "calculate", "verify"]
        )
        
        # Solution 2: Iterative refinement approach
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine through iterations.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration of multiple strategies
        sol3 = await self.flexible_custom(
            custom_instruction="Explore different solution paths simultaneously.",
            reasoning_pattern="parallel",
            steps=["strategy_a", "strategy_b", "compare"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # --- SCENSEMBLE: Select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- FINAL REVIEW: Improve the selected solution ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer