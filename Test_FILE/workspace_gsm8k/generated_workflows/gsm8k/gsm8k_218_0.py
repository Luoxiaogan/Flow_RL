# Workflow ID: gsm8k_218_0
# Benchmark: gsm8k
# Data Indices: [647, 877, 47]

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
        Generates three different solutions via varied reasoning strategies,
        then selects the best one using ScEnsemble. A final review ensures clarity.
        """
        # --- Step 1: Generate 3 diverse solutions using different Custom instructions ---
        solution1 = await self.custom(instruction="Solve step-by-step using arithmetic operations only.")
        solution2 = await self.custom(instruction="Break the problem into logical parts: identify knowns, unknowns, and apply relevant formulas.")
        solution3 = await self.custom(instruction="Use a systematic approach: define variables, write equations, solve step by step.")

        # --- Step 2: Ensembe the solutions to find the most consistent and accurate answer ---
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer