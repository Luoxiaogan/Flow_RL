# Workflow ID: gsm8k_35_1
# Benchmark: gsm8k
# Data Indices: [128, 270]

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
        Efficient and diverse workflow using parallel ensemble with FlexibleCustom.
        Generates 3 independent solutions via parallel reasoning, then selects the best one.
        This approach reduces reliance on a single reasoning path while maintaining simplicity.
        """
        # Step 1: Generate 3 different solutions using FlexibleCustom in parallel mode
        solutions = []
        for _ in range(3):
            solution = await self.flexible_custom(
                reasoning_pattern="parallel",
                steps=["identify_knowns", "formulate_plan", "execute_calculation", "check_consistency"],
                custom_instruction="Solve this problem by exploring multiple valid reasoning paths. Be clear and logical."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution