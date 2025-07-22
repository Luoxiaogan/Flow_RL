# Workflow ID: gsm8k_161_1
# Benchmark: gsm8k
# Data Indices: [57, 112, 689]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern with a single flexible custom step.
        It leverages the FlexibleCustom operator in iterative mode to refine the solution through multiple passes,
        focusing on systematic improvement rather than reflection or ensemble methods.
        """
        # Step 1: Use FlexibleCustom with iterative reasoning pattern to generate an initial solution
        # and progressively refine it over multiple iterations based on internal feedback loops
        refined_solution = await self.flexible_custom(
            custom_instruction="Begin by analyzing the problem, then solve it step-by-step. After each iteration, evaluate your approach for clarity and correctness.",
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "verify"],
            max_iterations=2
        )

        return refined_solution