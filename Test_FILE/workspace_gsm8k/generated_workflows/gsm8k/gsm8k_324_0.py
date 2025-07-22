# Workflow ID: gsm8k_324_0
# Benchmark: gsm8k
# Data Indices: [759, 832]

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
        Generates 3 different solutions via varied custom instructions, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple candidate solutions using different reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step by identifying known quantities and unknowns first."
            elif i == 1:
                instruction = "Use a systematic approach: define variables, set up equations, solve them logically."
            else:
                instruction = "Break down the problem into smaller sub-problems and solve each part independently."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to improve clarity and catch any remaining issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer