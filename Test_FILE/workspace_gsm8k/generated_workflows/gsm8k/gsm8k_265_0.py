# Workflow ID: gsm8k_265_0
# Benchmark: gsm8k
# Data Indices: [561, 673, 662]

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
        It generates three distinct solutions via different reasoning strategies,
        then selects the most consistent one using ScEnsemble, followed by a final review.
        """
        # --- Step 1: Generate multiple independent solutions using varied approaches ---
        solution_list = []
        
        # Solution 1: Direct calculation with clear breakdown
        sol1 = await self.custom(instruction="Solve the problem step-by-step, showing all calculations explicitly.")
        solution_list.append(sol1)

        # Solution 2: Use FlexibleCustom with sequential reasoning for structured logic
        sol2 = await self.flexible_custom(
            custom_instruction="Apply systematic reasoning: identify inputs, compute each part, sum total.",
            reasoning_pattern="sequential",
            steps=["identify_inputs", "compute_individuals", "sum_total"]
        )
        solution_list.append(sol2)

        # Solution 3: Use FlexibleCustom with iterative refinement to improve accuracy
        sol3 = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine your approach until you're confident in the result.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "refine_calculation", "final_check"],
            max_iterations=2
        )
        solution_list.append(sol3)

        # --- Step 2: Enforce consistency via ensemble selection ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final polish with Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer