# Workflow ID: gsm8k_247_0
# Benchmark: gsm8k
# Data Indices: [868, 454, 620]

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
        Generates 3 independent solutions with varied reasoning strategies,
        then selects the best one via ensemble, followed by a final review for polish.
        """
        # Step 1: Generate 3 diverse solutions using different custom instructions
        solution_list = []
        instructions = [
            "Break down the problem into clear steps: identify knowns, unknowns, and required calculations.",
            "Solve the problem as if you're teaching it to someone who has never seen this type of math before.",
            "Use dimensional analysis or unit-based reasoning to ensure all quantities are correctly handled."
        ]

        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to refine any remaining issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer