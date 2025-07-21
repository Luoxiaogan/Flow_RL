# Workflow ID: gsm8k_138_1
# Benchmark: gsm8k
# Data Indices: [875, 688, 379]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern.
        It starts with a basic solution and applies Review twice to progressively improve clarity, correctness, and completeness.
        The structure is simple but effective: initial solution → review → review → final answer.
        """
        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given. Then, determine what needs to be found. Finally, show your calculations clearly."
        )

        # Step 2: Apply iterative refinement — first review to catch errors or omissions
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second review for deeper improvement — focus on logical flow and precision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined