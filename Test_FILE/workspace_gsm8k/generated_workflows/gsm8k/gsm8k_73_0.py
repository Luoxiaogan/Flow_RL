# Workflow ID: gsm8k_73_0
# Benchmark: gsm8k
# Data Indices: [158, 102]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 independent solutions via different flexible patterns, then selects best.
        Final review ensures clarity and correctness.
        """
        # --- Parallel Ensemble: Generate 3 varied solutions ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve systematically by identifying key components first.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_relationships", "apply_math", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start rough, improve
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an initial estimate, then refine iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "evaluate", "refine"],
                    max_iterations=2
                )
            else:
                # Branching logic: consider multiple paths
                solution = await self.flexible_custom(
                    custom_instruction="Explore alternative interpretations of the problem structure.",
                    reasoning_pattern="branching",
                    steps=["analyze_options", "compare_approaches", "select_best"]
                )
            solution_list.append(solution)

        # --- Select best solution via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Final Review for polish and clarity ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer