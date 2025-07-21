# Workflow ID: gsm8k_63_0
# Benchmark: gsm8k
# Data Indices: [531, 111]

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
        It generates 3 independent solutions via varied instructions, then selects the best one.
        A final review ensures clarity and correctness before returning the result.
        """

        # --- STEP 1: Generate multiple candidate solutions using different reasoning styles ---
        solution_list = []
        instructions = [
            "Solve step-by-step by breaking down each part of the problem logically.",
            "Use systematic calculation: identify quantities, apply operations in order, verify steps.",
            "Think like a math tutor: explain each step clearly as if teaching someone new to the topic."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review for clarity, completeness, and error detection ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer