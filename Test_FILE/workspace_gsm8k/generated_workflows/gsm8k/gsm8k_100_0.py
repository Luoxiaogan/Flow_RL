# Workflow ID: gsm8k_100_0
# Benchmark: gsm8k
# Data Indices: [524, 274, 696]

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
        It generates three independent solutions via different reasoning strategies,
        then selects the most consistent one using ScEnsemble. Finally, it applies
        a review step to polish the final answer.
        """
        # --- Step 1: Generate three diverse solutions using different approaches ---
        solution_list = []

        # Solution 1: Use FlexibleCustom with a sequential reasoning pattern
        seq_solution = await self.flexible_custom(
            custom_instruction="Apply systematic problem decomposition.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Use FlexibleCustom with an iterative pattern for refinement
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with estimation, then refine through iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Use plain Custom with a creative, multi-step instruction
        creative_solution = await self.custom(
            instruction="Break down the problem into smaller parts, solve each part logically, "
                        "and then combine the results. Be explicit about your assumptions."
        )
        solution_list.append(creative_solution)

        # --- Step 2: Enforce consensus via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final polishing via Review ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer