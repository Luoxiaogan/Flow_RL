# Workflow ID: gsm8k_223_1
# Benchmark: gsm8k
# Data Indices: [357, 102]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and applies the Review operator twice
        to progressively enhance the solution — focusing on iterative improvement rather than reflection or ensemble.
        This differs fundamentally from the existing workflow by avoiding reflection-based guidance
        and instead relying solely on structured critique and revision in sequence.
        """
        # Step 1: Generate a basic, straightforward solution
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be direct and clear in your reasoning."
        )

        # Step 2: Apply first refinement — review to improve clarity and correctness
        refined_solution = await self.review(pre_solution=current_solution)

        # Step 3: Apply second refinement — further polish based on the first review
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution