# Workflow ID: gsm8k_385_1
# Benchmark: gsm8k
# Data Indices: [938, 730, 909]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern.
        It generates three distinct solutions using different reasoning strategies,
        then selects the most consistent one via ensemble. Finally, it applies a
        review step to polish the final answer — ensuring robustness and accuracy
        through diversity of thought and post-processing refinement.
        """

        # Step 1: Generate multiple independent solutions using varied prompts and patterns
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (focus on structured steps)
                solution = await self.flexible_custom(
                    custom_instruction="Break down the problem into clear logical steps.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (start rough, improve)
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an estimation, then refine your approach iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Flexible prompt-based reasoning (less rigid structure)
                solution = await self.custom(
                    instruction="Solve this problem by thinking through it as if you're teaching someone else."
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best-performing solution based on consistency and clarity
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to ensure correctness, clarity, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer