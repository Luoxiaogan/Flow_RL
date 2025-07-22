# Workflow ID: gsm8k_368_0
# Benchmark: gsm8k
# Data Indices: [903, 128]

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
        Generates 3 different solutions with varied reasoning approaches, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 independent solutions using different strategies ---
        solution_list = []
        instructions = [
            "Solve step-by-step by breaking down the problem into arithmetic operations.",
            "Use a systematic approach: identify quantities, apply operations in order, and verify each step.",
            "Think like a math tutor: explain your reasoning clearly as if teaching someone unfamiliar with the problem."
        ]

        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review to polish and ensure logical consistency ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer