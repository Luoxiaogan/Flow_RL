# Workflow ID: gsm8k_61_0
# Benchmark: gsm8k
# Data Indices: [172, 744]

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
        Diverse and robust workflow using Parallel Ensemble with iterative refinement.
        Generates 3 distinct solutions via varied reasoning patterns, then selects the best.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using different FlexibleCustom configurations
        solution_list = []
        
        # Solution 1: Sequential approach – clear step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Break down the problem systematically.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        
        # Solution 2: Iterative approach – refine from initial estimate
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial guess, then refine iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Parallel approach – explore multiple interpretations
        sol3 = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations of the problem.",
            reasoning_pattern="parallel",
            steps=["interpret", "evaluate", "compare"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for polish and error correction
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer