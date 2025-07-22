# Workflow ID: gsm8k_112_1
# Benchmark: gsm8k
# Data Indices: [604, 123, 848]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern with FlexibleCustom.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution and refine it over 2 passes.
        Step 2: If the refined solution seems incomplete or ambiguous, use Review to improve clarity and completeness.
        This avoids unnecessary parallelism while ensuring depth through structured iteration.
        """
        # --- ITERATIVE REFINEMENT USING FLEXIBLECUSTOM ---
        refined_solution = await self.flexible_custom(
            custom_instruction="Solve this problem by breaking it into steps: identify knowns, set up equations, solve, verify.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        # --- FINAL REVIEW FOR CLARITY AND COMPLETENESS ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer