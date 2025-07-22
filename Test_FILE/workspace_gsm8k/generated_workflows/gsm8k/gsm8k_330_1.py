# Workflow ID: gsm8k_330_1
# Benchmark: gsm8k
# Data Indices: [723, 537, 7]

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
        It generates multiple independent solutions in parallel, then selects the best one.
        This approach improves robustness by leveraging diverse reasoning paths without requiring iterative refinement or reflection.
        """
        # Step 1: Generate three independent solutions using different reasoning styles
        solution1 = await self.custom(
            instruction="Solve the problem step-by-step using a structured, formulaic approach. Break it into clear mathematical steps."
        )
        solution2 = await self.custom(
            instruction="Solve the problem by first identifying all given quantities and then determining what needs to be calculated next."
        )
        solution3 = await self.custom(
            instruction="Solve the problem as if you're explaining it to someone who is new to math — use plain language and logical flow."
        )

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return best_solution