# Workflow ID: gsm8k_6_1
# Benchmark: gsm8k
# Data Indices: [320, 284, 456]

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
        This is a diverse and effective workflow using the Iterative Refinement pattern with a Reflect-based loop.
        It starts with an initial solution, uses Reflect to critique it, then regenerates a better version based on that reflection.
        This creates a meta-cognitive loop — not just refining the answer, but also improving the reasoning process itself.
        The structure is fundamentally different from the existing workflow because:
          - It uses Reflect instead of Review for introspection (not just editing).
          - It combines Reflection + Custom regeneration in a loop (not just sequential review).
          - It leverages the new Reflect operator to guide improvement, rather than relying solely on iterative editing.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, solve the problem again with a focus on addressing the identified weaknesses."
        )

        # Step 4: Apply one final refinement using Review to polish the improved solution
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution