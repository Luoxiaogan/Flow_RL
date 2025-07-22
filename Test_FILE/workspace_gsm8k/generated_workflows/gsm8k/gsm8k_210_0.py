# Workflow ID: gsm8k_210_0
# Benchmark: gsm8k
# Data Indices: [902, 743]

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
        It generates three independent solutions with different reasoning strategies,
        then selects the best one via ScEnsemble. A final review ensures clarity and correctness.
        """

        # --- Step 1: Generate multiple solutions in parallel using varied approaches ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Step-by-step breakdown (sequential reasoning)
                instruction = "Break down the problem into clear steps, showing all calculations explicitly."
                solution = await self.flexible_custom(
                    custom_instruction=instruction,
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "compute", "verify"]
                )
            elif i == 1:
                # Strategy 2: Estimation-first approach (iterative refinement)
                instruction = "Start with an estimate, then refine your answer through logical checks."
                solution = await self.flexible_custom(
                    custom_instruction=instruction,
                    reasoning_pattern="iterative",
                    steps=["estimate", "check", "adjust"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Alternative method exploration (parallel thinking)
                instruction = "Solve using at least two different methods and compare results."
                solution = await self.flexible_custom(
                    custom_instruction=instruction,
                    reasoning_pattern="parallel",
                    steps=["method_a", "method_b", "compare"]
                )
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final review to polish clarity and catch any subtle errors ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer