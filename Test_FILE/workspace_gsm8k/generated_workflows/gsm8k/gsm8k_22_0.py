# Workflow ID: gsm8k_22_0
# Benchmark: gsm8k
# Data Indices: [954, 835, 909]

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
        It generates three independent solutions with varied reasoning strategies,
        then selects the best one via ScEnsemble. A final review ensures clarity and correctness.
        """
        # --- Generate 3 diverse solutions using different reasoning patterns ---
        solution_list = []
        
        # Solution 1: Sequential approach – systematic breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Solve step-by-step using logical deduction.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        
        # Solution 2: Iterative refinement – start simple, improve
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine it through multiple iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Parallel exploration – consider multiple interpretations
        sol3 = await self.flexible_custom(
            custom_instruction="Explore different ways to interpret the problem structure.",
            reasoning_pattern="parallel",
            steps=["interpretation_a", "interpretation_b", "compare"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # --- Select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer