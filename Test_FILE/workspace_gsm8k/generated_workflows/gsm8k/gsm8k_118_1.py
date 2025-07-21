# Workflow ID: gsm8k_118_1
# Benchmark: gsm8k
# Data Indices: [335, 601, 387]

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
        Parallel Ensemble + Final Review Workflow:
        Generates three diverse solutions using different reasoning strategies (sequential, iterative, branching),
        then selects the best one via ensemble. A final review ensures clarity and correctness.
        This approach enhances robustness by leveraging multiple perspectives and reducing reliance on any single reasoning path.
        """
        # Step 1: Generate three independent solutions using FlexibleCustom with different patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential: Break into clear logical steps
                solution = await self.flexible_custom(
                    custom_instruction="Solve this step-by-step with explicit reasoning for each part.",
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "solve", "verify"]
                )
            elif i == 1:
                # Iterative: Start with an estimate, refine it
                solution = await self.flexible_custom(
                    custom_instruction="Begin with a rough estimate, then refine your answer through iterations.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Branching: Consider alternative interpretations or paths
                solution = await self.flexible_custom(
                    custom_instruction="Explore multiple possible approaches to the problem, then choose the most valid one.",
                    reasoning_pattern="branching",
                    steps=["identify_approaches", "evaluate", "select"]
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final refinement — ensure clarity, completeness, and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer