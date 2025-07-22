# Workflow ID: gsm8k_86_1
# Benchmark: gsm8k
# Data Indices: [334, 519]

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
        It generates three independent solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent and accurate one.
        Finally, it applies a single review step for polish and clarity — ensuring robustness
        through diversity of initial approaches and post-processing refinement.
        """
        # Step 1: Generate multiple solutions in parallel using varied strategies
        solution_list = []
        strategies = [
            "Break down the problem into clear steps: identify inputs, operations, and outputs.",
            "Solve by first calculating unit cost, then scaling up to total batches or plays.",
            "Use dimensional analysis: track units (liters, kg, dollars) throughout each calculation."
        ]
        
        for i, strategy in enumerate(strategies):
            solution = await self.custom(
                instruction=f"Apply this reasoning approach: {strategy}"
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best among the three diverse solutions
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via Review to improve clarity and correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution