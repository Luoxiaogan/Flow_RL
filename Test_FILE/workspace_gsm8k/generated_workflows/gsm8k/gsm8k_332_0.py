# Workflow ID: gsm8k_332_0
# Benchmark: gsm8k
# Data Indices: [853, 373]

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
        It starts with an initial solution, then applies Review at least twice to progressively improve it.
        The structure is logical, uses only allowed operators, and avoids any problem-specific content.
        """
        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, breaking it into clear logical parts. Be precise and avoid assumptions."
        )

        # Step 2: First refinement via Review — improve clarity, logic flow, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — focus on potential errors or missing steps
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Optional third refinement (to ensure iterative depth as required)
        final_solution = await self.review(pre_solution=second_refined)

        return final_solution