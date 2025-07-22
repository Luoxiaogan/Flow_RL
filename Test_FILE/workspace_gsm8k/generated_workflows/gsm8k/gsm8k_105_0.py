# Workflow ID: gsm8k_105_0
# Benchmark: gsm8k
# Data Indices: [264, 107]

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
        Generates 3 different solutions via varied instructions, ensembles them,
        then applies a final review for polish.
        """
        # Step 1: Generate 3 independent solutions using different reasoning styles
        solution_list = []
        instructions = [
            "Solve step-by-step by identifying key quantities and relationships first.",
            "Break the problem into smaller sub-problems, solve each, then combine.",
            "Use algebraic modeling: define variables and write equations based on the given text."
        ]
        
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to refine clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer