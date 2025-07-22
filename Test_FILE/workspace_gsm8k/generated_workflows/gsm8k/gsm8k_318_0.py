# Workflow ID: gsm8k_318_0
# Benchmark: gsm8k
# Data Indices: [116, 372, 288]

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
        It generates 3 independent solutions with varied reasoning strategies,
        then selects the best one via ensemble, followed by a final review for polish.
        """
        # Step 1: Generate multiple solutions using different custom instructions
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this step-by-step using clear arithmetic operations. Break down each part of the problem logically."
            elif i == 1:
                instruction = "Approach the problem as if you're teaching someone who is new to math. Explain every assumption and calculation clearly."
            else:
                instruction = "Use a structured plan: identify what’s given, determine what’s needed, apply relevant formulas or logic, and verify your answer."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for refinement — improves clarity and catches any lingering errors
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer