# Workflow ID: gsm8k_43_1
# Benchmark: gsm8k
# Data Indices: [368, 268]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using the Review operator.
        This approach emphasizes progressive improvement through structured critique—ideal for problems requiring careful reasoning and error detection.
        """
        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into clear parts and explain each reasoning step thoroughly."
        )

        # --- Step 2: First Iteration of Refinement ---
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second Iteration of Refinement ---
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        # --- Step 4: Final Output ---
        final_solution = refined_solution_2

        return final_solution