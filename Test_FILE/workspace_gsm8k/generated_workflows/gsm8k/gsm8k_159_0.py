# Workflow ID: gsm8k_159_0
# Benchmark: gsm8k
# Data Indices: [64, 584, 682]

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
        It starts with a simple initial solution, then applies Review twice to progressively improve it.
        The structure ensures logical flow, uses only generic operators, and avoids any problem-specific content.
        """
        # Step 1: Generate an initial solution using a basic instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: First refinement via Review — improves clarity, logic, or completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — further enhances accuracy and structure
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined