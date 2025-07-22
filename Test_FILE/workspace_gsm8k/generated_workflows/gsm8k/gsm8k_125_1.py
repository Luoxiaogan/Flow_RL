# Workflow ID: gsm8k_125_1
# Benchmark: gsm8k
# Data Indices: [51, 921, 189]

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
        This is a diverse and efficient workflow using the 'Parallel Ensemble' pattern.
        It generates multiple independent solutions in parallel (via loop), then selects the best one.
        This approach improves robustness by leveraging diversity of reasoning paths without needing iterative refinement or reflection.
        It's simpler than the existing workflow because it avoids meta-cognition (reflect/review) and instead uses ensemble-based selection.
        """
        # Step 1: Generate 3 different solutions using varied prompts to encourage diverse reasoning
        solutions = []
        for i in range(3):
            prompt = (
                "Solve this problem step-by-step with clear reasoning. "
                "Focus on identifying known quantities, applying correct operations, and showing all calculations."
            )
            solution = await self.custom(instruction=prompt)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        return best_solution