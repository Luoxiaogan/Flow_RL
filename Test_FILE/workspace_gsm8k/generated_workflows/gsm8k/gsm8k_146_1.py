# Workflow ID: gsm8k_146_1
# Benchmark: gsm8k
# Data Indices: [883, 842]

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
        Iterative Refinement Workflow: Start with a basic solution and improve it through two rounds of review.
        This pattern emphasizes progressive enhancement over exploration or ensemble methods.
        
        Step 1: Generate an initial solution using a simple Custom call.
        Step 2: Apply Review twice to refine the solution iteratively—each time improving clarity, logic, and completeness.
        Step 3: Return the final refined solution as the answer.
        
        Why this is different:
        - No parallel ensembling (unlike existing).
        - No reflection-guided regeneration (unlike existing).
        - Uses only one initial solution path, but enhances it systematically via repeated review.
        - Focuses on iterative improvement within a single chain of reasoning rather than branching or selecting from multiple paths.
        """

        # --- INITIAL SOLUTION ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be concise but clear in your reasoning."
        )

        # --- ITERATIVE REFINEMENT: First Review ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- ITERATIVE REFINEMENT: Second Review ---
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined