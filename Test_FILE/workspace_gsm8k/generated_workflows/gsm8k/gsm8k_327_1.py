# Workflow ID: gsm8k_327_1
# Benchmark: gsm8k
# Data Indices: [210, 774, 919]

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
        Efficient and logically distinct workflow using Iterative Refinement with FlexibleCustom.
        Instead of ensemble or reflection-based regeneration, this uses a single iterative loop
        with structured reasoning steps to progressively improve the solution — minimizing redundancy
        while maximizing logical progression from initial idea to final answer.
        
        Key differences from existing:
        - No parallel generation (fan-out/fan-in)
        - No reflection-guided regeneration
        - Uses iterative refinement via FlexibleCustom with max_iterations=2
        - Simpler structure: 1 flexible custom call with iterative pattern
        - More efficient than ensemble + reflection combo
        """
        # --- ITERATIVE REFINEMENT USING FLEXIBLECUSTOM ---
        refined_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, focusing on clarity and correctness.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return refined_solution