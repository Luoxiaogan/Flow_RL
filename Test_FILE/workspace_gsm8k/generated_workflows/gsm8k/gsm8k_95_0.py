# Workflow ID: gsm8k_95_0
# Benchmark: gsm8k
# Data Indices: [364, 206, 697]

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
        It generates 3 different solutions with varied reasoning strategies,
        then ensembles them to find the most consistent answer. Finally, it reviews
        the best solution for clarity and correctness.
        """
        # Generate 3 independent solutions using different reasoning styles
        solution_list = []
        instructions = [
            "Solve step-by-step: identify each action in sequence, calculate intermediate totals, and verify consistency.",
            "Break the problem into sub-problems: handle each person's contribution separately before combining.",
            "Use a structured approach: define variables for knowns and unknowns, then apply arithmetic operations systematically."
        ]
        
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Enforce consensus via ensemble — pick the most accurate one
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Final review to polish the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer