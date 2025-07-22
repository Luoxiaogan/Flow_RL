# Workflow ID: gsm8k_393_0
# Benchmark: gsm8k
# Data Indices: [58, 351, 355]

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
        Generates 3 independent solutions via FlexibleCustom with different reasoning patterns,
        then selects the best one using ScEnsemble. A final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns ---
        solutions = []

        # Solution 1: Sequential reasoning – clear step-by-step breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"]
        )
        solutions.append(seq_solution)

        # Solution 2: Iterative refinement – start with rough estimate, improve
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with an initial estimate, then refine your answer through iteration.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Solution 3: Parallel approach – consider multiple strategies simultaneously
        par_solution = await self.flexible_custom(
            custom_instruction="Explore multiple solution paths in parallel to increase robustness.",
            reasoning_pattern="parallel",
            steps=["strategy_a", "strategy_b", "strategy_c"]
        )
        solutions.append(par_solution)

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer