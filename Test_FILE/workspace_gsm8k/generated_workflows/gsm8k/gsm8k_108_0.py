# Workflow ID: gsm8k_108_0
# Benchmark: gsm8k
# Data Indices: [342, 861]

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
        Generates 3 independent solutions with varied reasoning instructions,
        then selects the best one via ensemble, followed by a final review for quality assurance.
        """
        solution_list = []

        # Generate three different solutions using custom instructions that encourage diverse approaches
        instructions = [
            "Solve step-by-step: identify quantities first, then compute totals. Be explicit about each animal group.",
            "Break the problem into parts: calculate total enclosures per species, then multiply by animals per enclosure.",
            "Use a table-based approach: list each species, count enclosures, then calculate total animals."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Final review to improve clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer