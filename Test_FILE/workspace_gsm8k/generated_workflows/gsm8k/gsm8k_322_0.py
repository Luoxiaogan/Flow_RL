# Workflow ID: gsm8k_322_0
# Benchmark: gsm8k
# Data Indices: [251, 792]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This pattern first generates an initial solution, then reflects on it to identify potential flaws or improvements,
        and finally uses an iterative flexible custom operator to refine the solution step-by-step.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each part of your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use iterative FlexibleCustom to systematically improve the solution
        refined_solution = await self.flexible_custom(
            custom_instruction="Use the following reflection to guide a structured, iterative refinement process.",
            previous_results=[initial_solution],
            reasoning_pattern="iterative",
            steps=["analyze", "refine", "verify"],
            max_iterations=2
        )

        return refined_solution