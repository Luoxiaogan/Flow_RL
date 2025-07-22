# Workflow ID: gsm8k_225_0
# Benchmark: gsm8k
# Data Indices: [594, 716, 618]

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
        It generates three independent solutions via varied instructions, then selects the best one.
        A final review ensures clarity and correctness before returning.
        """
        # Step 1: Generate 3 different solutions using varied reasoning strategies
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by identifying key ratios and applying proportional reasoning."
            elif i == 1:
                instruction = "Break the problem into smaller logical parts: what's given, what's unknown, and how they relate."
            else:
                instruction = "Use a structured approach: define variables, write equations, solve systematically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via Review to improve clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer