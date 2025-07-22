# Workflow ID: gsm8k_40_1
# Benchmark: gsm8k
# Data Indices: [341, 255, 611]

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
        This is a diverse and complex workflow using the 'Reflect and Regenerate' pattern as the core logic.
        
        Key Differences from Existing:
        - Uses Reflect + Custom in a meta-cognitive loop (not just one reflection).
        - Employs iterative refinement via FlexibleCustom with 'iterative' pattern.
        - Starts with a single solution, reflects, then regenerates — no ensemble or parallelism.
        - The reflection directly informs a structured, multi-step regeneration process.
        
        This approach mimics how humans improve reasoning: generate → critique → rebuild → refine.
        """

        # Step 1: Generate an initial solution using a flexible custom operator with a sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps: identify knowns, unknowns, relationships, and compute.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "formulate_equation", "solve"]
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite, just analyze
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new solution via a flexible custom operator in iterative mode
        # This allows for multiple passes of refinement based on the reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: {reflection}, solve again with improved clarity and structure.",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_assumptions", "recompute", "verify"],
            max_iterations=2
        )

        # Step 4: Final review to polish logic, language, and completeness
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer