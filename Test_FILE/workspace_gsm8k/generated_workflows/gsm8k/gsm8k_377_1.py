# Workflow ID: gsm8k_377_1
# Benchmark: gsm8k
# Data Indices: [337, 702, 165]

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
        Efficient and logically distinct workflow using Iterative Refinement with a single Custom call followed by Review.
        This approach prioritizes clarity and correctness through focused improvement rather than parallel exploration or reflection-based regeneration.
        
        Key differences from existing:
        - No parallel ensemble or reflection-based regeneration
        - Uses iterative refinement (Review) in a minimal loop for efficiency
        - Single initial solution → review cycle instead of multiple paths
        - Simpler logic flow: generate → improve → return (no branching or complex selection)
        """

        # Step 1: Generate initial solution with clear step-by-step instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify all known quantities. Second, determine what needs to be calculated. Third, perform the necessary calculations. Finally, state the answer clearly."
        )

        # Step 2: Use Review to refine the solution — this is the core iterative step
        refined_solution = await self.review(pre_solution=initial_solution)

        return refined_solution