# Workflow ID: gsm8k_145_1
# Benchmark: gsm8k
# Data Indices: [164, 317, 140]

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
        then selects the most consistent one via ensemble. A final review ensures clarity
        and correctness before returning the result.
        """

        # Step 1: Generate multiple candidate solutions in parallel using varied approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem by breaking it into clear, logical steps and verifying each step."
            elif i == 1:
                instruction = "First identify all known quantities and unknowns, then set up equations or proportional relationships."
            else:
                instruction = "Use estimation first to get a rough answer, then refine your approach based on exact calculations."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best-performing solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution — improve clarity, fix minor errors, ensure completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer