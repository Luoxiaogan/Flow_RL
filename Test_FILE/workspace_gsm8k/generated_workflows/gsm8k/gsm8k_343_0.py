# Workflow ID: gsm8k_343_0
# Benchmark: gsm8k
# Data Indices: [451, 600]

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
        It generates three independent solutions with varied reasoning strategies,
        then selects the best one via ensemble, followed by a final review for polish.
        """
        # Step 1: Generate multiple candidate solutions using different approaches
        solution_list = []
        instructions = [
            "Solve step-by-step: first identify what's given, then set up an equation, and finally compute.",
            "Break the problem into parts: define variables, write relationships, solve systematically.",
            "Think like a math tutor: explain each logical transition clearly as you go."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement — review the best solution to catch any lingering errors or unclear steps
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer