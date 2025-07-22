# Workflow ID: gsm8k_221_1
# Benchmark: gsm8k
# Data Indices: [489, 148]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Robust parallel ensemble workflow using diverse reasoning strategies.
        This design generates 3 independently reasoned solutions with different prompts,
        then selects the most consistent one via ScEnsemble. A final review ensures clarity.
        This approach avoids single-point failures and leverages diversity for accuracy.
        """
        # Step 1: Generate multiple independent solutions using varied reasoning strategies
        solution_pool = []
        strategies = [
            "Solve by breaking the problem into clear steps and checking each calculation.",
            "Approach this as a word problem: identify quantities, relationships, and operations first.",
            "Think like a teacher explaining this to a student—use plain language and logical progression."
        ]

        for strategy in strategies:
            solution = await self.custom(instruction=strategy)
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and correctness
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Final review to polish and clarify the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer