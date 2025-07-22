# Workflow ID: gsm8k_155_0
# Benchmark: gsm8k
# Data Indices: [894, 944, 292]

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
        Generates 3 different solutions with varied reasoning strategies, then selects the best one.
        A final review ensures quality before return.
        """
        # --- STEP 1: Generate 3 diverse solutions using different reasoning patterns ---
        solution_list = []

        # Solution 1: Sequential approach — step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear, sequential steps.",
            reasoning_pattern="sequential",
            steps=["understand", "identify", "compute", "verify"]
        )
        solution_list.append(sol1)

        # Solution 2: Iterative refinement — start with estimation, improve
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an initial estimate, then refine your answer through multiple passes.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "finalize"],
            max_iterations=2
        )
        solution_list.append(sol2)

        # Solution 3: Parallel thinking — generate multiple perspectives in one go
        sol3 = await self.flexible_custom(
            custom_instruction="Consider multiple interpretations or methods for solving this problem simultaneously.",
            reasoning_pattern="parallel",
            steps=["method_a", "method_b", "method_c"]
        )
        solution_list.append(sol3)

        # --- STEP 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review for polish and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer