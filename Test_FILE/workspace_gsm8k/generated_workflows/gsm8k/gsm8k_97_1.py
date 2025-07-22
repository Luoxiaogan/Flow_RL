# Workflow ID: gsm8k_97_1
# Benchmark: gsm8k
# Data Indices: [734, 382]

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
        It generates three distinct solutions using different reasoning strategies (sequential, iterative, branching),
        then selects the most consistent one via ScEnsemble. A final review ensures clarity and correctness.
        This approach enhances robustness by leveraging multiple reasoning paths and consensus-based selection.
        """
        # Step 1: Generate three independent solutions using different FlexibleCustom configurations
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: clear step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve this problem by breaking it into logical steps.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "formulate_plan", "execute_steps", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start with rough estimate, improve iteratively
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an approximate answer, then refine it through multiple passes.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Branching logic: consider alternative interpretations or assumptions
                solution = await self.flexible_custom(
                    custom_instruction="Explore possible interpretations of the problem and choose the most plausible path.",
                    reasoning_pattern="branching",
                    steps=["analyze_assumptions", "evaluate_options", "select_best", "solve"]
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on consistency across all attempts
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the selected solution — improves clarity and fixes minor issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer