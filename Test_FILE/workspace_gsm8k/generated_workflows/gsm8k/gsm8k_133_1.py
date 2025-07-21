# Workflow ID: gsm8k_133_1
# Benchmark: gsm8k
# Data Indices: [950, 710]

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
        This workflow uses a novel structure: Iterative Refinement with a single initial solution.
        1. Generate an initial solution using Custom.
        2. Use Review to refine it once — this is efficient and avoids over-engineering.
        3. Reflect on the revised solution to catch any subtle flaws or missed assumptions.
        4. Finally, use FlexibleCustom in iterative mode to polish the answer further based on reflection.
        
        Why it's different:
        - No parallel ensemble (unlike existing).
        - No multiple custom calls upfront.
        - Uses a tight feedback loop: Review → Reflect → FlexibleCustom (iterative).
        - Efficient: Only 3 main steps after initial solve, keeps complexity low but effective.
        """
        # Step 1: Initial solution via Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: Improve with one round of Review
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Reflect on the refined solution for hidden issues
        reflection = await self.reflect(pre_solution=refined_solution)

        # Step 4: Final polish using iterative FlexibleCustom guided by reflection
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: '{reflection}'. Now improve the solution through iterative refinement.",
            reasoning_pattern="iterative",
            steps=["validate_logic", "check_units", "ensure_completeness"],
            max_iterations=2
        )

        return final_solution