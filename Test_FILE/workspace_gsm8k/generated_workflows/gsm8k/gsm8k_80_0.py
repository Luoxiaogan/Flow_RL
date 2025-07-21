# Workflow ID: gsm8k_80_0
# Benchmark: gsm8k
# Data Indices: [787, 199, 332]

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
        Three different reasoning strategies are applied independently, then the best is selected.
        A final review ensures clarity and correctness.
        """
        # Generate three distinct solutions using varied approaches
        solution1 = await self.flexible_custom(
            custom_instruction="Use step-by-step decomposition: identify knowns, unknowns, and apply arithmetic operations sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_equation", "compute", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Apply iterative refinement: start with an estimate, then improve through logical checks.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "validate", "refine"],
            max_iterations=2
        )

        solution3 = await self.custom(
            instruction="Solve by breaking the problem into smaller sub-problems, solving each in isolation, then combining results."
        )

        # Ensembling: pick the most consistent and accurate solution
        ensemble_solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        # Final review to polish and ensure clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer