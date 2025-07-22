# Workflow ID: gsm8k_313_1
# Benchmark: gsm8k
# Data Indices: [20, 758]

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
        This workflow uses a novel structure: Iterative Refinement via FlexibleCustom with structured reasoning steps.
        It avoids ensemble or reflection-based regeneration. Instead, it leverages the built-in iterative pattern of FlexibleCustom
        to progressively refine a single solution path — efficient, logical, and distinct from the existing parallel+reflect approach.
        
        Key differences from existing:
        - No parallel generation (no ScEnsemble over multiple candidates)
        - No reflection-guided regeneration
        - Uses only one main solution stream, iteratively improved via internal steps
        - Simpler logic flow: one operator call with built-in iteration
        """

        # Use FlexibleCustom in iterative mode with 2 refinement steps
        refined_solution = await self.flexible_custom(
            custom_instruction="Solve this problem step-by-step using a systematic approach.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution