# Workflow ID: gsm8k_162_0
# Benchmark: gsm8k
# Data Indices: [452, 439]

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
        It generates 3 different solutions via varied reasoning approaches, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using parallel ensemble ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Use sequential FlexibleCustom for structured step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Break down the problem into clear steps.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_units", "compute_intermediate", "derive_final"]
                )
            elif i == 1:
                # Use iterative FlexibleCustom to refine an initial estimate
                solution = await self.flexible_custom(
                    custom_instruction="Start with a rough estimate, then improve it iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Use Custom with a creative prompt to encourage alternative thinking
                solution = await self.custom(
                    instruction="Solve this by imagining you're teaching someone who knows nothing about units. Be very clear."
                )
            solution_list.append(solution)

        # --- Step 2: Enforce consensus via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final review for polish and error detection ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer