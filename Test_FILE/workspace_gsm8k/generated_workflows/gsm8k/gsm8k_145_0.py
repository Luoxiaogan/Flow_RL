# Workflow ID: gsm8k_145_0
# Benchmark: gsm8k
# Data Indices: [657, 388]

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
        It generates 3 distinct solutions via different reasoning strategies,
        then selects the best one using ScEnsemble, followed by a final review for polish.
        """
        # --- Step 1: Generate 3 independent solutions using varied approaches ---
        solution_list = []
        instructions = [
            "Solve step-by-step using algebraic equations. Define variables clearly.",
            "Break the problem into smaller logical steps. Think like a detective solving a mystery.",
            "Use a visual model or diagram to represent the situation before calculating."
        ]

        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # --- Step 2: Enforce consensus via ensemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final refinement through review ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer