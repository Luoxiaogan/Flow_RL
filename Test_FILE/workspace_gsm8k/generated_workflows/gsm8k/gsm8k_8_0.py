# Workflow ID: gsm8k_8_0
# Benchmark: gsm8k
# Data Indices: [75, 277, 900]

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
        then selects the best one via ScEnsemble, followed by a final review for refinement.
        """
        # Step 1: Generate multiple solutions using different approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step using basic arithmetic operations only."
            elif i == 1:
                instruction = "Break down the problem into parts, label each part clearly, and solve systematically."
            else:
                instruction = "Think like a math teacher: explain your steps as if teaching someone who is new to word problems."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for polish and clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer