# Workflow ID: gsm8k_10_1
# Benchmark: gsm8k
# Data Indices: [547, 548, 343]

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
        Efficient and diverse workflow using Iterative Refinement with a single initial solution.
        This approach avoids parallelism or ensembling (unlike the existing), instead focusing on one clear path:
        1. Generate an initial solution
        2. Use Review to refine it once — this is lightweight but effective for most problems
        3. Return the improved result

        Why this is different:
        - No parallel solutions or ensemble selection
        - No reflection-based regeneration
        - Simpler logic: generate → review → done
        - Uses only one loop iteration (no multiple attempts), making it efficient
        - Leverages Review's ability to fix common errors like missing steps or unit issues
        """
        # Step 1: Generate an initial solution with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into logical steps. Show your work clearly and include all units."
        )

        # Step 2: Improve the solution using Review — this handles reasoning gaps or calculation errors
        refined_solution = await self.review(pre_solution=initial_solution)

        return refined_solution