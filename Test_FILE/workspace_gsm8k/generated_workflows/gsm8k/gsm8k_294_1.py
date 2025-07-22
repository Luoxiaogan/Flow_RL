# Workflow ID: gsm8k_294_1
# Benchmark: gsm8k
# Data Indices: [215, 26, 644]

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
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it reviews the best
        solution for clarity and accuracy — ensuring both diversity in approach and final quality.
        """
        # Step 1: Generate multiple solutions in parallel using varied instructions
        solution_list = []
        prompts = [
            "Solve the problem by breaking it into clear, step-by-step logical parts.",
            "Approach this as if you're teaching someone unfamiliar with the topic — explain each step thoroughly.",
            "Use an estimation-first method: make a rough guess, then refine it systematically."
        ]
        
        for prompt in prompts:
            solution = await self.custom(instruction=prompt)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to improve clarity, fix subtle issues, or enhance explanation
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution