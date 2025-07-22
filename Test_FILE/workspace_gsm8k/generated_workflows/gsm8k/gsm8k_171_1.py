# Workflow ID: gsm8k_171_1
# Benchmark: gsm8k
# Data Indices: [982, 368]

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
        Iterative Refinement with Reflective Guidance: 
        This workflow uses a meta-cognitive loop where each refinement is informed by critical reflection.
        It's fundamentally different from the existing workflow because it doesn't just refine blindly — 
        it first reflects on the solution's weaknesses before generating the next iteration.
        This introduces intentional improvement based on self-awareness rather than mechanical revision.
        """

        # Step 1: Generate an initial solution using a structured sequential approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_formula", "compute_result"],
            custom_instruction="Solve step-by-step: break down inputs, compute each part, then combine."
        )

        # Step 2: Reflect on the initial solution — critique assumptions, logic gaps, or clarity issues
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a targeted second solution (not just generic review)
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem focusing on addressing these points. Be precise and systematic."
        )

        # Step 4: Apply another round of review for final polish — this time refining structure and completeness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution