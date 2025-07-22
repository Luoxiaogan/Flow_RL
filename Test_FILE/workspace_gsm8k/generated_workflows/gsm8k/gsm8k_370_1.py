# Workflow ID: gsm8k_370_1
# Benchmark: gsm8k
# Data Indices: [409, 814]

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
        This is a diverse and robust workflow using:
        1. Iterative Refinement (via FlexibleCustom with iterative pattern)
        2. Reflect-and-Regenerate (using the new Reflect operator to guide improvement)
        
        Key differences from existing:
        - Uses iterative refinement instead of parallel ensemble
        - Introduces meta-cognition via Reflect before regenerating
        - Does NOT use ScEnsemble — instead relies on internal feedback loops
        - Combines two distinct patterns: Iterative + Reflect-and-Regenerate
        """

        # --- Step 1: Use FlexibleCustom in iterative mode for structured, step-by-step refinement ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving the problem by identifying key variables and constraints.",
            reasoning_pattern="iterative",
            steps=["identify", "plan", "solve", "verify"],
            max_iterations=2
        )

        # --- Step 2: Critically reflect on the solution to uncover hidden assumptions or errors ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate a new solution based on the reflection, focusing on fixing flaws ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Use this insight to construct a corrected, improved solution. Be explicit about how you addressed the issues raised."
        )

        return final_answer