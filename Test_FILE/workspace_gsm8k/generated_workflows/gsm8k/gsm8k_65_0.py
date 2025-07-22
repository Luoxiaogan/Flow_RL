# Workflow ID: gsm8k_65_0
# Benchmark: gsm8k
# Data Indices: [757, 671, 379]

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
        then selects the best one via ScEnsemble, followed by a final review for polish.
        """
        # Step 1: Generate 3 different solutions using parallel approaches
        solution_list = []
        instructions = [
            "Solve step-by-step using clear arithmetic reasoning.",
            "Break down the problem into logical components first, then compute.",
            "Apply a systematic approach: identify inputs, apply transformations, verify."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via Review to ensure clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer