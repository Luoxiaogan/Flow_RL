# Workflow ID: gsm8k_105_1
# Benchmark: gsm8k
# Data Indices: [560, 965]

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
        This is a diverse and robust workflow using:
        1. Parallel Ensemble with varied reasoning strategies (each custom call uses a different approach)
        2. Final review to polish the selected solution
        """

        # Step 1: Generate 3 solutions using different reasoning patterns via FlexibleCustom
        solutions = []
        for i in range(3):
            if i == 0:
                # Use sequential reasoning: break into steps explicitly
                solution = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "compute", "verify"],
                    custom_instruction="Solve the problem by following a strict sequence of logical steps."
                )
            elif i == 1:
                # Use iterative refinement from the start — simulate multiple passes internally
                solution = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2,
                    custom_instruction="Begin with an estimate, then refine it twice before finalizing."
                )
            else:
                # Use branching logic — consider alternative interpretations first
                solution = await self.flexible_custom(
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "explore_alternatives", "select_best"],
                    custom_instruction="Consider multiple ways to interpret the problem and choose the most reasonable one."
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Apply a final review to improve clarity, precision, or catch any lingering errors
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution