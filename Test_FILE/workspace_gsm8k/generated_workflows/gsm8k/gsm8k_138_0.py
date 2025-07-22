# Workflow ID: gsm8k_138_0
# Benchmark: gsm8k
# Data Indices: [777, 916]

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
        Generates 3 distinct solutions via different FlexibleCustom patterns,
        then selects the best one using ScEnsemble, followed by a final review.
        """
        # Step 1: Generate 3 different solutions using varied reasoning patterns
        solution_list = []
        
        # Solution 1: Sequential reasoning (step-by-step breakdown)
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this problem methodically, breaking it into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify"]
        )
        
        # Solution 2: Iterative refinement (start with rough estimate, improve)
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an approximate approach, then refine your answer through multiple iterations.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration (consider multiple interpretations or methods)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore multiple possible approaches to solve this problem and synthesize the most reliable result.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare_and_select"]
        )
        
        solution_list.extend([sol1, sol2, sol3])

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review for polish and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer