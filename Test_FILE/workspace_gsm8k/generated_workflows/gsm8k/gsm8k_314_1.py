# Workflow ID: gsm8k_314_1
# Benchmark: gsm8k
# Data Indices: [729, 282]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates multiple independent solutions (fan-out), then selects the best one (fan-in).
        This approach improves robustness by leveraging diversity in reasoning paths without requiring iterative refinement or reflection.
        """
        # Step 1: Generate three different initial solutions using varied prompts
        solution1 = await self.custom(
            instruction="Solve the problem step-by-step with a focus on identifying all quantities first."
        )
        solution2 = await self.custom(
            instruction="Break the problem into smaller logical units. Solve each unit separately before combining."
        )
        solution3 = await self.custom(
            instruction="Use a visual or diagrammatic approach to model the problem mathematically."
        )

        # Step 2: Use ScEnsemble to evaluate and select the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return best_solution