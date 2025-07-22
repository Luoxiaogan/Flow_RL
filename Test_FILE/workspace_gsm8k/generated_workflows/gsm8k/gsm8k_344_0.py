# Workflow ID: gsm8k_344_0
# Benchmark: gsm8k
# Data Indices: [435, 272]

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
        This is a diverse workflow using Iterative Refinement with FlexibleCustom for structured reasoning.
        Step 1: Generate an initial solution using a sequential reasoning pattern.
        Step 2: Apply Review twice to progressively refine the solution.
        """
        # --- STEP 1: Initial Solution via Sequential Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what needs to be solved and break it into logical steps.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "define_variables", "formulate_equation", "solve"]
        )

        # --- STEP 2: Iterative Refinement with Review (at least two times) ---
        refined_solution_1 = await self.review(pre_solution=initial_solution)
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2