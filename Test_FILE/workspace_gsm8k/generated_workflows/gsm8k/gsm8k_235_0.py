# Workflow ID: gsm8k_235_0
# Benchmark: gsm8k
# Data Indices: [401, 92]

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
        Generates 3 different solutions via varied reasoning strategies, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple solutions using different approaches
        solution_list = []
        instructions = [
            "Solve the problem by breaking it into clear steps and verifying each calculation.",
            "Use systematic arithmetic: identify fixed costs, variable costs, and apply operations in order.",
            "Think like a math tutor: explain your reasoning as if teaching someone new to the topic."
        ]
        
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the answer and ensure logical flow
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer