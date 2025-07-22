# Workflow ID: gsm8k_208_1
# Benchmark: gsm8k
# Data Indices: [542, 946]

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
        This is a diverse workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and applies the `Review` operator twice
        to progressively improve it — focusing on clarity, logical consistency, and completeness.
        This structure ensures deep refinement without branching or ensembling,
        offering a clean, stepwise path to a high-quality solution.
        """

        # Step 1: Generate an initial solution using a basic sequential approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "set_up", "solve", "check"],
            custom_instruction="Solve the problem by breaking it into clear steps: understand the question, set up variables, solve, and verify your answer."
        )

        # Step 2: First review – improve clarity and correctness of the initial solution
        first_revision = await self.review(pre_solution=initial_solution)

        # Step 3: Second review – refine further, focusing on assumptions, edge cases, and logical flow
        second_revision = await self.review(pre_solution=first_revision)

        return second_revision