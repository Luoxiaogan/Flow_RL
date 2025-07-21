# Workflow ID: gsm8k_187_0
# Benchmark: gsm8k
# Data Indices: [410, 113]

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
        self.reflect = operator.Reflect(self.config, self.problem) # New operator
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        """
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        Generates 3 different solutions via varied reasoning strategies, then ensembles them.
        A final review ensures clarity and correctness.
        """
        solution_list = []

        # Generate three distinct solutions using different approaches
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step using arithmetic operations only. Focus on clear, linear reasoning."
            elif i == 1:
                instruction = "Break the problem into parts: identify knowns, unknowns, and apply relevant formulas or logic."
            else:
                instruction = "Use a structured approach: define variables, set up equations, solve systematically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Enforce consistency with ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Final refinement through review for polish and error detection
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer