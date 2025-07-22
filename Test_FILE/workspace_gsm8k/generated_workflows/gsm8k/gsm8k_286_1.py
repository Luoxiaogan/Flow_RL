# Workflow ID: gsm8k_286_1
# Benchmark: gsm8k
# Data Indices: [581, 467, 222]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern.
        It generates multiple independent solutions in parallel and selects the best one.
        This approach improves robustness by leveraging diversity in reasoning strategies
        without requiring iterative refinement or reflection — making it efficient and effective.
        """
        # Step 1: Generate 3 different solutions using independent reasoning paths
        solution1 = await self.custom(
            instruction="Solve the problem step-by-step. Focus on identifying all quantities first."
        )
        solution2 = await self.custom(
            instruction="Break the problem into smaller sub-problems. Solve each one individually."
        )
        solution3 = await self.custom(
            instruction="Use a structured method: define knowns, unknowns, then apply operations logically."
        )

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return final_solution