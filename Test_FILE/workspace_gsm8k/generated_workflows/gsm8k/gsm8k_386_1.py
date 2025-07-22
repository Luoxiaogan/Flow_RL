# Workflow ID: gsm8k_386_1
# Benchmark: gsm8k
# Data Indices: [780, 233]

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
        Diverse and effective workflow using the Iterative Refinement pattern.
        Step 1: Generate an initial solution with a flexible custom operator using a sequential reasoning pattern.
        Step 2: Apply the Review operator twice to progressively refine the solution — each time improving clarity, correctness, or completeness.
        This structure ensures deep iterative improvement without parallelism or ensemble selection, offering a fundamentally different logic from the existing workflow.
        """
        # --- INITIAL SOLUTION VIA SEQUENTIAL FLEXIBLE CUSTOM ---
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem into clear analytical steps. Identify all given values and relationships before solving."
        )

        # --- ITERATIVE REFINEMENT (REVIEW TWICE) ---
        refined_solution_1 = await self.review(pre_solution=initial_solution)
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2