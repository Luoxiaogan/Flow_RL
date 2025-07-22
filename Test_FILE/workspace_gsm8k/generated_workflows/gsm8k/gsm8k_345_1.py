# Workflow ID: gsm8k_345_1
# Benchmark: gsm8k
# Data Indices: [890, 824]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions using different reasoning strategies,
        then uses ScEnsemble to select the most accurate one. Finally, it applies a
        single review step to polish the chosen solution — ensuring robustness through diversity
        and consistency checks while maintaining clarity.
        """
        # Step 1: Generate multiple solutions in parallel using varied instructions
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem by breaking it into clear, sequential steps with explicit calculations."
            elif i == 1:
                instruction = "Approach this as a word problem: identify quantities, relationships, and compute step-by-step."
            else:
                instruction = "Use a structured method: define variables, set up equations, solve systematically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ensemble to pick the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via review for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer