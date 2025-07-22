# Workflow ID: gsm8k_351_1
# Benchmark: gsm8k
# Data Indices: [874, 882, 234]

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
        It generates three distinct solutions using different reasoning strategies via FlexibleCustom,
        then selects the most consistent one using ScEnsemble. Finally, it performs a final review
        to polish the chosen solution — ensuring robustness through diversity of approach.
        """

        # Step 1: Generate multiple independent solutions using parallel reasoning patterns
        solutions = []
        for i in range(3):
            # Use FlexibleCustom with different reasoning patterns to ensure varied logic paths
            if i == 0:
                # Sequential: Clear step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve the problem by breaking it into clear, sequential steps.",
                    reasoning_pattern="sequential",
                    steps=["understand", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative: Start with estimation, refine iteratively
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an estimate, then improve it through refinement.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Branching: Consider multiple interpretations or cases
                solution = await self.flexible_custom(
                    custom_instruction="Consider alternative approaches or interpretations before deciding on a path.",
                    reasoning_pattern="branching",
                    steps=["analyze_options", "choose_best", "execute"]
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final Review to improve clarity, correctness, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer