# Workflow ID: gsm8k_201_1
# Benchmark: gsm8k
# Data Indices: [52, 575, 617]

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
        Iterative Refinement Workflow: Generate an initial solution, then apply Review at least twice to progressively improve it.
        This mimics how humans refine their reasoning — first draft, then critique and revise, then refine again.
        
        Key differences from existing workflow:
        - No parallel ensemble or reflection-guided regeneration
        - Pure iterative improvement using only Review (no Reflect or ScEnsemble)
        - Focus on progressive refinement through multiple passes
        - Uses a simple loop with fixed iterations instead of branching logic
        """

        # Step 1: Generate an initial solution using Custom
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Apply iterative refinement via Review at least twice
        for iteration in range(2):  # Two rounds of review and revision
            current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Return the final refined solution
        return current_solution