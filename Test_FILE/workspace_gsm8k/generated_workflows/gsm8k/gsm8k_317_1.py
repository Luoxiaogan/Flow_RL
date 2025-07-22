# Workflow ID: gsm8k_317_1
# Benchmark: gsm8k
# Data Indices: [534, 986, 786]

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
        Diverse workflow using the 'Iterative Refinement' pattern with two rounds of review.
        This structure emphasizes progressive improvement through repeated critique and refinement,
        without relying on reflection or ensemble — creating a fundamentally different logic path.
        """
        # Step 1: Generate an initial solution using a simple sequential approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, breaking it into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"]
        )

        # Step 2: Apply the first round of iterative refinement via Review
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Apply a second round of refinement to further improve clarity and correctness
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution