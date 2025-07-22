# Workflow ID: gsm8k_355_1
# Benchmark: gsm8k
# Data Indices: [586, 645]

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
        It generates three distinct solutions using varied reasoning strategies via FlexibleCustom,
        then selects the most consistent one with ScEnsemble. A final review ensures clarity and correctness.
        This approach improves robustness by leveraging multiple independent solution paths.
        """

        # Step 1: Generate 3 different solutions using parallel reasoning patterns
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential step-by-step decomposition (like a textbook method)
                solution = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"],
                    custom_instruction="Break down the problem into clear, sequential steps."
                )
            elif i == 1:
                # Strategy 2: Iterative refinement — start with estimation, then improve
                solution = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["initial_approach", "refine", "finalize"],
                    max_iterations=2,
                    custom_instruction="Begin with an estimate, then refine your answer through two iterations."
                )
            else:
                # Strategy 3: Branching logic — consider alternative interpretations first
                solution = await self.flexible_custom(
                    reasoning_pattern="branching",
                    steps=["analyze_options", "choose_best", "compute"],
                    custom_instruction="Explore different ways to interpret the problem before solving."
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution — ensure it's well-explained and free of logical gaps
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer