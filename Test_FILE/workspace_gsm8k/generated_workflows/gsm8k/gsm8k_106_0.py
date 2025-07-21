# Workflow ID: gsm8k_106_0
# Benchmark: gsm8k
# Data Indices: [129, 768, 259]

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
        This is a diverse and iterative refinement-based workflow.
        It starts with an initial solution, then refines it twice using the Review operator.
        The structure ensures progressive improvement without relying on ensembling or reflection.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given and what needs to be found. Then, apply logical reasoning to derive the answer."
        )

        # Step 2: First refinement — review the initial solution for clarity, accuracy, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on the first review
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined