# Workflow ID: gsm8k_182_1
# Benchmark: gsm8k
# Data Indices: [568, 704, 479]

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
        Parallel Ensemble + Final Review Workflow:
        1. Generate 3 diverse solutions using different reasoning strategies via FlexibleCustom.
        2. Use ScEnsemble to select the most consistent and accurate solution.
        3. Perform a final review to polish clarity and correctness.
        
        This approach improves robustness by exploring multiple reasoning paths and selecting the best one — fundamentally different from iterative refinement.
        """
        # Step 1: Generate 3 distinct solutions using varied reasoning patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve this problem using a structured, sequential approach.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative reasoning: refine through multiple passes
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an estimate and refine iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Branching reasoning: explore alternatives based on intermediate checks
                solution = await self.flexible_custom(
                    custom_instruction="Use branching logic to consider multiple valid approaches.",
                    reasoning_pattern="branching",
                    steps=["identify_options", "evaluate", "choose_best"]
                )
            solutions.append(solution)

        # Step 2: Enforce consistency by selecting the best solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final polish — ensure the selected solution is clear, complete, and logically sound
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer