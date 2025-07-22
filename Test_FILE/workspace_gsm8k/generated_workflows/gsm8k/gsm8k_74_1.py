# Workflow ID: gsm8k_74_1
# Benchmark: gsm8k
# Data Indices: [94, 988]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Iterative Refinement.
        1. Generate an initial solution using FlexibleCustom in sequential mode for structured reasoning.
        2. Reflect on it to identify potential flaws or missed assumptions.
        3. Use that reflection to guide a new Custom call for a targeted improvement.
        4. Then apply iterative refinement (Review) up to 2 times to polish the answer further.
        This creates a meta-cognitive loop: generate → reflect → improve → refine.
        """
        # Step 1: Generate a structured initial solution using FlexibleCustom in sequential mode
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply a step-by-step decomposition of the problem.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new solution attempt—this is the "regenerate" phase
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem focusing on addressing these points. Be thorough and precise."
        )

        # Step 4: Apply iterative refinement using Review to progressively enhance clarity and correctness
        current_solution = improved_solution
        for _ in range(2):  # Two rounds of review/refinement
            current_solution = await self.review(pre_solution=current_solution)

        return current_solution