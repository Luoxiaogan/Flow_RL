# Workflow ID: gsm8k_291_1
# Benchmark: gsm8k
# Data Indices: [473, 801, 11]

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
        Parallel Ensemble + Final Review Workflow for General Mathematical Problem Solving
        This workflow explores multiple reasoning strategies in parallel, then selects the best solution
        using ensemble evaluation. A final review step ensures clarity and correctness before output.
        
        Key differences from existing workflow:
        - Uses parallel generation (3 different approaches) instead of iterative refinement
        - Employs ScEnsemble to select the most consistent answer among diverse solutions
        - Includes a final review step to polish the selected solution
        """

        # Step 1: Generate 3 independent solutions using varied strategies
        solution_list = []
        strategies = [
            "Break the problem into smaller steps and solve each one systematically.",
            "Use visual modeling or diagrams to represent relationships between quantities.",
            "Apply reverse engineering: start from the expected outcome and work backward."
        ]
        
        for strategy in strategies:
            solution = await self.flexible_custom(
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction=strategy
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via Review to improve clarity and logic flow
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer