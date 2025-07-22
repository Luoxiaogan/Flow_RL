# Workflow ID: gsm8k_41_0
# Benchmark: gsm8k
# Data Indices: [84, 588, 504]

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
        It generates three different solutions via varied reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for refinement.
        """
        # --- Step 1: Generate multiple solutions using parallel ensemble ---
        solution_list = []
        instructions = [
            "Solve the problem step-by-step using clear arithmetic operations.",
            "Break the problem into parts, solve each part independently, then combine.",
            "Use a structured approach: identify knowns, unknowns, relationships, and compute."
        ]

        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to select the most consistent solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final review for quality improvement ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer