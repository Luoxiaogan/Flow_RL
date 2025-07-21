# Workflow ID: gsm8k_90_0
# Benchmark: gsm8k
# Data Indices: [755, 967]

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
        Generates 3 different solutions via varied custom instructions and flexible patterns,
        then selects the best one using ScEnsemble. Final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 distinct solutions using different approaches ---
        solution_list = []

        # Solution 1: Use sequential FlexibleCustom for structured breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using logical analysis.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Use iterative FlexibleCustom to refine an initial attempt
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with a rough estimate, then refine through iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "final_answer"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Use Custom with a creative, alternative framing
        alt_solution = await self.custom(
            instruction="Solve this by imagining how a teacher would explain it to a student—clearly and in simple terms."
        )
        solution_list.append(alt_solution)

        # --- Step 2: Ensemble selection ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final review for polish and accuracy ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer