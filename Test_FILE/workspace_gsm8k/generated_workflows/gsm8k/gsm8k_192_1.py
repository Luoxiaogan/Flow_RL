# Workflow ID: gsm8k_192_1
# Benchmark: gsm8k
# Data Indices: [273, 450]

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
        Robust parallel ensemble workflow with diverse reasoning strategies.
        Generates 3 independently reasoned solutions using different FlexibleCustom patterns,
        then selects the best one via ScEnsemble. Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple candidate solutions using different reasoning strategies
        solution_pool = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (step-by-step logic)
                solution = await self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "formulate_equation", "compute", "verify"],
                    custom_instruction="Solve this math problem by identifying known quantities, forming a mathematical expression, computing it, and verifying your result."
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (improve step-by-step)
                solution = await self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "final_check"],
                    max_iterations=2,
                    custom_instruction="Start with an estimate, refine it logically, and confirm the final answer."
                )
            else:
                # Strategy 3: Branching logic (consider multiple paths)
                solution = await self.flexible_custom(
                    reasoning_pattern="branching",
                    steps=["analyze_options", "evaluate_paths", "choose_best"],
                    custom_instruction="Consider different approaches to solving the problem, evaluate their validity, and select the most logical path."
                )
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Final review to polish clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer