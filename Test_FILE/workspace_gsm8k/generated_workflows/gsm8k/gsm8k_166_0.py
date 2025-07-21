# Workflow ID: gsm8k_166_0
# Benchmark: gsm8k
# Data Indices: [821, 467, 545]

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
        This is a diverse and effective workflow using the Iterative Refinement pattern.
        It starts with a basic solution, then applies Review twice to progressively improve it.
        The structure ensures logical flow while maintaining generality across math problems.
        """
        # Step 1: Generate an initial solution using Custom with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into smaller parts."
        )

        # Step 2: First refinement via Review — improve clarity, logic, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — address any remaining ambiguities or errors
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined