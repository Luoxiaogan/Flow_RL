# Workflow ID: gsm8k_90_1
# Benchmark: gsm8k
# Data Indices: [184, 891, 135]

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
        Iterative Refinement with Reflective Guidance: 
        This workflow uses a reflective loop to guide iterative improvements — not just mechanical review, but meta-cognitive critique that informs each refinement step.
        
        Key differences from the existing workflow:
        - Uses `Reflect` to generate critical feedback before each refinement (not just blind review).
        - Applies 2 rounds of refinement, but each is informed by reflection — making it more strategic than mechanical.
        - Does NOT use ScEnsemble or parallel processing; instead, focuses on deep, guided iteration.
        """

        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly and logically."
        )

        # Step 2: First round of improvement — reflect first, then refine
        reflection_1 = await self.reflect(pre_solution=initial_solution)
        refined_1 = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection_1}'. Now, provide an improved version of the solution that addresses these points."
        )

        # Step 3: Second round — reflect again on the first refinement, then improve further
        reflection_2 = await self.reflect(pre_solution=refined_1)
        refined_2 = await self.custom(
            instruction=f"Based on this reflection: '{reflection_2}', revise the previous solution to make it more accurate, complete, and logically sound."
        )

        return refined_2