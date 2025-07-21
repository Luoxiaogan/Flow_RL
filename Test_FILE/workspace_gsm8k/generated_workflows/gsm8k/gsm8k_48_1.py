# Workflow ID: gsm8k_48_1
# Benchmark: gsm8k
# Data Indices: [275, 373, 334]

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
        This approach emphasizes progressive improvement through structured feedback loops rather than parallel exploration or reflection-based regeneration.
        """
        # --- STEP 1: Initial Solution via Custom ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and explain each part clearly."
        )

        # --- STEP 2: First Iteration of Refinement (Review) ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- STEP 3: Second Iteration of Refinement (Review again) ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- STEP 4: Final Output ---
        final_answer = second_refined

        return final_answer