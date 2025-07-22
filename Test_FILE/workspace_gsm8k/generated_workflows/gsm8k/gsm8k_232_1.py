# Workflow ID: gsm8k_232_1
# Benchmark: gsm8k
# Data Indices: [908, 1]

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
        Diverse and efficient workflow using Iterative Refinement with a single Custom step.
        This approach is simpler than the existing one but uses a structured iterative pattern via FlexibleCustom.
        It avoids parallelism and ensemble logic entirely — instead, it focuses on refining one solution iteratively.
        This is logically distinct from the original (which used fan-out/fan-in + reflection).
        """
        # --- STEP 1: Use FlexibleCustom in iterative mode to solve the problem through progressive refinement ---
        solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by first forming a clear plan, then executing it step-by-step. "
                              "If the initial result seems off, revise your assumptions and try again.",
            reasoning_pattern="iterative",
            steps=["plan", "execute", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return solution