# Workflow ID: gsm8k_269_1
# Benchmark: gsm8k
# Data Indices: [975, 279]

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
        This is a diverse and complex workflow using the Iterative Refinement pattern.
        Step 1: Generate an initial solution using a simple Custom call.
        Step 2: Apply Review twice in sequence to progressively refine it—first for clarity and structure, then for accuracy and completeness.
        This mimics how humans improve solutions through multiple passes of reflection and editing.
        """
        # --- INITIAL SOLUTION ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear, concise, and logically structured."
        )

        # --- ITERATIVE REFINEMENT: First pass ---
        first_refinement = await self.review(
            pre_solution=initial_solution
        )

        # --- ITERATIVE REFINEMENT: Second pass ---
        second_refinement = await self.review(
            pre_solution=first_refinement
        )

        return second_refinement