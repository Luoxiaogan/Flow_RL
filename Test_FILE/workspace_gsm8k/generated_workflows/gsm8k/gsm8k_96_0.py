# Workflow ID: gsm8k_96_0
# Benchmark: gsm8k
# Data Indices: [987, 237, 607]

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
        Generates 3 independent solutions via varied instructions, ensembles them,
        then applies a final review for refinement.
        """
        # --- Step 1: Generate 3 diverse solutions using different reasoning strategies ---
        solution_list = []
        instructions = [
            "Break the problem into clear mathematical steps and solve each one sequentially.",
            "Think like a financial planner: identify all costs and revenues first, then compute totals.",
            "Solve by modeling the problem as a real-world transaction with multiple components."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review for polish and clarity ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer