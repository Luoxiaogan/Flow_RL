# Workflow ID: gsm8k_175_1
# Benchmark: gsm8k
# Data Indices: [790, 516]

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
        This workflow uses the Iterative Refinement pattern with a single FlexibleCustom call.
        It leverages the iterative reasoning pattern in FlexibleCustom to progressively improve the solution
        over multiple passes without needing external ensembling or reflection-based regeneration.
        
        Key differences from existing:
        - No parallel ensemble (fan-out/fan-in) — instead, a single flexible custom with internal iteration
        - No separate reflection step — refinement happens internally via structured steps
        - Simpler control flow: one loop inside FlexibleCustom vs. multiple explicit steps
        - Efficient and focused: avoids redundant generation of multiple solutions
        """
        # --- ITERATIVE REFINEMENT WITH FLEXIBLECUSTOM ---
        solution = await self.flexible_custom(
            custom_instruction="Solve the problem by iterating through refined approaches.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2  # Two iterations for refinement
        )

        return solution