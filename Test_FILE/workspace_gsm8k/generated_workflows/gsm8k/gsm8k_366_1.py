# Workflow ID: gsm8k_366_1
# Benchmark: gsm8k
# Data Indices: [978, 294, 258]

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
        then selects the most consistent one via ensemble. Finally, it applies a review
        to polish the chosen solution for clarity and correctness — ensuring robustness
        through diversity of approach and post-processing refinement.
        """

        # Step 1: Generate multiple candidate solutions in parallel using varied strategies
        solution_pool = []
        strategies = [
            ("Break down step-by-step with clear explanations", "sequential"),
            ("Use estimation first, then precise calculation", "iterative"),
            ("Consider alternative interpretations before solving", "branching")
        ]

        for instruction, pattern in strategies:
            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and logic
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Final review to refine language, fix subtle errors, or improve clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer