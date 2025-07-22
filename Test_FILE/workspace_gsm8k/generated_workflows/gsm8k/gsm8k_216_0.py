# Workflow ID: gsm8k_216_0
# Benchmark: gsm8k
# Data Indices: [60, 980]

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
        Generates 3 different solutions via varied instructions, ensembles them,
        then applies a final review for consistency and clarity.
        """

        # Step 1: Generate multiple independent solutions using different reasoning strategies
        solution_list = []
        instructions = [
            "Solve step-by-step by setting up an equation based on percentage decrease.",
            "Break the problem into parts: identify what 4% represents numerically, then find the original amount.",
            "Use proportional reasoning: if 96% equals 48 ounces, what does 100% equal?"
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for clarity, logical flow, and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer