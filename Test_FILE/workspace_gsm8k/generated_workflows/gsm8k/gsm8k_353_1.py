# Workflow ID: gsm8k_353_1
# Benchmark: gsm8k
# Data Indices: [420, 518, 917]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. A final review ensures clarity
        and correctness — making this approach robust against single-point failures in reasoning.
        """
        # Step 1: Generate multiple independent solutions using varied instructions
        solution_list = []
        strategies = [
            "Solve step-by-step with clear explanations of each calculation.",
            "Break the problem into smaller subproblems and solve them sequentially.",
            "Use a structured plan: identify knowns, unknowns, formula, then compute."
        ]
        
        for strategy in strategies:
            solution = await self.custom(instruction=strategy)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer