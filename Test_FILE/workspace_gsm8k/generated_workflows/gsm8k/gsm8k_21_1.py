# Workflow ID: gsm8k_21_1
# Benchmark: gsm8k
# Data Indices: [554, 221, 349]

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
        It generates three distinct solutions using different reasoning strategies,
        then selects the most consistent one via ensemble, followed by a final review for refinement.
        This approach increases robustness by leveraging multiple perspectives.
        """
        # Step 1: Generate three independent solutions using different flexible custom configurations
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (focus on step-by-step logic)
                sol = await self.flexible_custom(
                    custom_instruction="Solve the problem by breaking it into clear, sequential steps.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (start with estimation, then improve)
                sol = await self.flexible_custom(
                    custom_instruction="Begin with an estimate, then refine your answer through iterative improvements.",
                    reasoning_pattern="iterative",
                    steps=["initial_approach", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Branching logic (consider multiple paths or assumptions)
                sol = await self.flexible_custom(
                    custom_instruction="Explore multiple possible interpretations of the problem and resolve them systematically.",
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "evaluate_paths", "select_best", "conclude"]
                )
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to select the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer