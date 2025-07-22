# Workflow ID: gsm8k_284_0
# Benchmark: gsm8k
# Data Indices: [684, 391]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates 3 independent solutions with different reasoning strategies,
        then selects the best one via ensemble, followed by a final review for polish.
        """
        solutions = []

        # Generate three diverse initial solutions using different flexible custom patterns
        for i in range(3):
            if i == 0:
                # Sequential approach: step-by-step decomposition
                solution = await self.flexible_custom(
                    custom_instruction="Solve systematically",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start rough, improve
                solution = await self.flexible_custom(
                    custom_instruction="Begin with estimation, refine iteratively",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Branching logic: consider multiple paths
                solution = await self.flexible_custom(
                    custom_instruction="Explore alternative interpretations before deciding",
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "evaluate_options", "choose_best"]
                )
            solutions.append(solution)

        # Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to ensure clarity, correctness, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer