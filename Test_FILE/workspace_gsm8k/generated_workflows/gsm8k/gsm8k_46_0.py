# Workflow ID: gsm8k_46_0
# Benchmark: gsm8k
# Data Indices: [482, 718]

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
        Generates 3 different solutions via varied reasoning strategies, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # --- STEP 1: Generate multiple independent solutions using parallel ensemble ---
        solution_list = []
        instructions = [
            "Solve step-by-step by breaking down the problem into smaller parts.",
            "Use algebraic modeling to represent relationships between variables.",
            "Start with an estimate, then refine the answer through logical deduction."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Optional but recommended: Review the best solution for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer